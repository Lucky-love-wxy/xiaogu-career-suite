"""截图识别文字：在本机用 RapidOCR 把图片转成文字，图片不落盘、不发给第三方。

设计见 notes/2026-10-13-图片识别.md：
- 识别结果只回填到输入框，由用户核对后自己发送；这里不判断它是 JD 还是简历，下游流程一行不改。
- 引擎延迟加载：agent 核心仍只依赖标准库，没装 rapidocr 的环境（如只跑测试）不受影响。
- 每张图在一个用完即退的子进程里识别：onnxruntime 识别一张 1080×2400 截图要占约 650MB，
  而且常驻进程里内存只涨不退（实测 36 张后 1.4GB）。服务器只有 2GB，子进程退出才能把内存全部还给系统；
  代价是每张多约 0.3 秒加载模型。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
import unicodedata

# resume_tools 在小谷 agent 核心目录（../web）；识别子进程是直接运行本文件的，也要能找到它
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "web"))
from pathlib import Path

from resume_tools import SECTION_HEADING  # 简历栏目标题（教育经历、项目经历……）必须单独成行，否则认不出整份简历

MAX_BYTES = 6 * 1024 * 1024
# 只认常见截图格式的文件头，不信任前端传来的类型
MAGIC = {b"\x89PNG": "png", b"\xff\xd8\xff": "jpeg", b"RIFF": "webp"}

_engine = None
_lock = threading.Lock()  # 同一时间只跑一个识别子进程，峰值内存不叠加
TIMEOUT = 60


class OcrError(ValueError):
    pass


class OcrUnavailable(RuntimeError):
    """识别环境本身有问题（没装 rapidocr、子进程崩溃或超时），不是用户图片的问题。"""


def image_kind(data: bytes) -> str | None:
    for head, kind in MAGIC.items():
        if data.startswith(head) and (kind != "webp" or data[8:12] == b"WEBP"):
            return kind
    return None


def _get_engine():
    global _engine
    if _engine is None:
        from rapidocr import RapidOCR  # 延迟导入：加载模型约 1 秒
        _engine = RapidOCR()
    return _engine


# 手机截图顶部的状态栏（时间、信号、电量）和只有符号的行，对理解岗位没有用
STATUS_BAR = re.compile(r"^(?:\d{1,2}:\d{2}.*|(?=.*\d)[\dA-Za-z%•·.…@<>|中 ]{1,8})$")
HAS_WORD = re.compile(r"[\u4e00-\u9fffA-Za-z0-9]")
# 招聘 App 底部的按钮，整行完全相同才删
BUTTONS = {"立即沟通", "继续沟通", "感兴趣", "投递简历", "立即投递", "举报"}


SENTENCE_END = tuple("。；;：:！!？?")
WRAP_RATIO = 0.8  # 和本图最长一行比，长度达到八成才算“被屏幕折行”，标题、短句不受影响
# 下一行是新条目的开头就不接（BOSS 条目、简历要点常不带句末标点）；OCR 常把小圆点识别成“。”
ITEM_START = re.compile(r"^(?:\d+[.、．)）]|[（(][\d一二三四五六七八九十]+[)）]|[一二三四五六七八九十]+[、.．]|[-•·●◦。])")
WRAP_MIN = 28  # 显示宽度（汉字算 2）；手机竖屏一行约 18–24 个汉字，整张图都是短行时（没有折行）不接


def width(line: str) -> int:
    """按显示宽度算行长：英文、数字比汉字窄，按字数算会把“2022.09-20”这类满宽行误判成短行。"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in line)


def clean(lines: list[str]) -> str:
    """去掉明显的界面杂字，并把被手机屏幕折断的句子接回去；正文一个字不改（错字留给用户在输入框里核对）。"""
    kept = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or not HAS_WORD.search(line) or line in BUTTONS:
            continue
        if i < 4 and STATUS_BAR.match(line):  # 只在最顶上几行判状态栏，避免误删正文里的“15-30K”之类
            continue
        kept.append(line)
    if not kept:
        return ""
    # 折行接回：不接的话，JD 原句会被拆成半句，小谷引用原文时只能引半句（2026-10-13 真实截图验证发现）
    full = max(width(line) for line in kept)
    merged = [kept[0]]
    for prev, line in zip(kept, kept[1:]):  # 按上一行原始长度判断，不用接过之后的长度
        if full >= WRAP_MIN and width(prev) >= full * WRAP_RATIO and not prev.endswith(SENTENCE_END) \
                and not ITEM_START.match(line) and not SECTION_HEADING.match(line):
            merged[-1] += line
        else:
            merged.append(line)
    return "\n".join(merged)


def recognize(data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise OcrError("图片太大了，单张请小于 6MB")
    if image_kind(data) is None:
        raise OcrError("只支持 PNG、JPG、WebP 格式的图片")
    with _lock:
        try:
            done = subprocess.run([sys.executable, str(Path(__file__).resolve())], input=data,
                                  capture_output=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            raise OcrUnavailable("识别超时") from None
        except OSError as exc:  # 子进程都起不来（解释器路径失效等）
            raise OcrUnavailable(str(exc)) from None
    if done.returncode != 0:
        raise OcrUnavailable(done.stderr.decode("utf-8", "replace")[-300:])
    # 只认最后一行的 JSON：rapidocr 会往输出里打日志
    lines = done.stdout.decode("utf-8").strip().splitlines()
    return clean(json.loads(lines[-1])["lines"])


if __name__ == "__main__":
    # 子进程入口：从标准输入读一张图，最后一行输出识别出的原始文字行；图片只在内存里
    result = _get_engine()(sys.stdin.buffer.read())
    print(json.dumps({"lines": list(result.txts or [])}, ensure_ascii=False))
