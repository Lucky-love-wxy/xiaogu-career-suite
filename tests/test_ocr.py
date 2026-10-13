"""截图识别（web/ocr.py + /api/ocr）：格式校验、杂字清理、登录与扣费边界，以及识别结果能被当成招聘说明存入会话。
真识别用例需要 rapidocr 和一个中文字体来现场生成截图，缺了就跳过。"""

import base64
import io
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT / "tests"))
import agent  # noqa: E402
import ocr  # noqa: E402

try:
    from test_platform import PlatformCase
except unittest.SkipTest:
    PlatformCase = None

FONTS = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"]
JD_LINES = ["13:42", "5G 100", "产品经理（校招）", "15-25K", "职位描述：", "1. 负责用户增长相关功能的需求调研与方案设计；",
            "2. 与研发、设计协作推进项目上线；", "任职要求：本科及以上学历，2026届毕业生", "立即沟通"]


def screenshot(lines: list[str]) -> bytes | None:
    """现场画一张白底黑字的“手机截图”；没有 Pillow 或中文字体就返回 None。"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    font_path = next((f for f in FONTS if Path(f).exists()), None)
    if not font_path:
        return None
    font = ImageFont.truetype(font_path, 40)
    img = Image.new("RGB", (1080, 120 + 90 * len(lines)), "white")
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((60, 60 + 90 * i), line, fill="black", font=font)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def has_engine() -> bool:
    try:
        import rapidocr  # noqa: F401
        return True
    except ImportError:
        return False


class CleanTests(unittest.TestCase):
    def test_rejects_non_images(self):
        with self.assertRaises(ocr.OcrError):
            ocr.recognize(b"%PDF-1.7 not an image")
        self.assertEqual(ocr.image_kind(b"\x89PNG\r\n\x1a\n"), "png")
        self.assertEqual(ocr.image_kind(b"RIFF\x00\x00\x00\x00WEBPVP8 "), "webp")
        self.assertIsNone(ocr.image_kind(b"RIFF\x00\x00\x00\x00WAVEfmt "))

    def test_rejects_oversized(self):
        with self.assertRaises(ocr.OcrError):
            ocr.recognize(b"\x89PNG" + b"0" * ocr.MAX_BYTES)

    def test_drops_status_bar_and_symbols_but_keeps_body(self):
        text = ocr.clean(["13:42", "5GI 100", "<", "外贸业务员", "15-30K", "1-3年大专", "•••", "大专", "PM"])
        self.assertEqual(text.splitlines(), ["外贸业务员", "15-30K", "1-3年大专", "大专", "PM"])

    def test_rejoins_lines_wrapped_by_the_screen(self):
        # 满宽且没以句号结尾的行是被屏幕折断的，接回整句；标题、短行和按钮不受影响
        lines = ["游戏策划", "任职要求：", "1. 学历专业：本科及以上学历，专业不限，计算机、", "数字媒体、设计等相关专业优先；",
                 "2. 熟悉1-2款主流游戏的核心玩法、系统设计、用户", "生态等；", "立即沟通"]
        self.assertEqual(ocr.clean(lines).splitlines(), [
            "游戏策划", "任职要求：", "1. 学历专业：本科及以上学历，专业不限，计算机、数字媒体、设计等相关专业优先；",
            "2. 熟悉1-2款主流游戏的核心玩法、系统设计、用户生态等；"])

    def test_status_bar_rule_only_applies_at_top(self):
        # 正文里单独一行的数字（如“2026”）不能被当成状态栏删掉
        lines = ["岗位", "职责", "要求", "说明", "2026"]
        self.assertIn("2026", ocr.clean(lines))


@unittest.skipUnless(has_engine(), "没装 rapidocr")
class RecognizeTests(unittest.TestCase):
    def test_screenshot_becomes_a_job_description(self):
        image = screenshot(JD_LINES)
        if image is None:
            self.skipTest("没有 Pillow 或中文字体")
        text = ocr.recognize(image)
        self.assertIn("产品经理", text)
        self.assertIn("任职要求", text)
        self.assertNotIn("13:42", text)
        # 识别出的文字用户核对后发出，要能被当成招聘说明存进会话
        session = agent.Session()
        self.assertIn("job", session.absorb("帮我看看这个岗位：\n" + text))


@unittest.skipIf(PlatformCase is None, "缺少 web/requirements-dev.txt")
class OcrApiTests(PlatformCase or unittest.TestCase):
    def test_requires_login(self):
        from fastapi.testclient import TestClient
        self.assertEqual(TestClient(self.app).post("/api/ocr", json={"image": ""}).status_code, 401)

    def test_bad_payload_is_400(self):
        client = self.login()
        self.assertEqual(client.post("/api/ocr", json={"image": "不是base64!!"}).status_code, 400)
        pdf = base64.b64encode(b"%PDF-1.7").decode()
        res = client.post("/api/ocr", json={"image": pdf})
        self.assertEqual(res.status_code, 400)
        self.assertIn("PNG", res.json()["error"])

    def test_maintenance_blocks_ocr(self):
        client = self.login()
        self.store.set_flag("maintenance", "1", "test")
        png = base64.b64encode(b"\x89PNG\r\n\x1a\n").decode()
        self.assertEqual(client.post("/api/ocr", json={"image": png}).status_code, 503)

    @unittest.skipUnless(has_engine(), "没装 rapidocr")
    def test_recognizes_without_charging(self):
        image = screenshot(JD_LINES)
        if image is None:
            self.skipTest("没有 Pillow 或中文字体")
        client = self.login()
        before = client.get("/api/me").json()["balance"]
        res = client.post("/api/ocr", json={"image": "data:image/png;base64," + base64.b64encode(image).decode()})
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIn("职位描述", res.json()["text"])
        self.assertEqual(client.get("/api/me").json()["balance"], before)  # 本机识别，不扣额度


if __name__ == "__main__":
    unittest.main()
