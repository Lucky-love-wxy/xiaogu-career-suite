"""截图识别文字：在本机用 RapidOCR 把图片转成文字，图片不落盘、不发给第三方。

设计见 notes/2026-10-13-图片识别.md：
- 识别结果只回填到输入框，由用户核对后自己发送；这里不判断它是 JD 还是简历，下游流程一行不改。
- 引擎延迟加载：agent 核心仍只依赖标准库，没装 rapidocr 的环境（如只跑测试）不受影响。
"""

from __future__ import annotations

import re
import threading

MAX_BYTES = 6 * 1024 * 1024
# 只认常见截图格式的文件头，不信任前端传来的类型
MAGIC = {b"\x89PNG": "png", b"\xff\xd8\xff": "jpeg", b"RIFF": "webp"}

_engine = None
_lock = threading.Lock()  # 引擎只加载一次；识别也串行，避免多请求同时占满 CPU 和内存


class OcrError(ValueError):
    pass


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
WRAP_MIN = 14  # 手机竖屏一行约 18–24 个汉字；整张图都是短行时（没有折行）不接


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
    full = max(len(line) for line in kept)
    merged = [kept[0]]
    for prev, line in zip(kept, kept[1:]):  # 按上一行原始长度判断，不用接过之后的长度
        if full >= WRAP_MIN and len(prev) >= full * WRAP_RATIO and not prev.endswith(SENTENCE_END):
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
        result = _get_engine()(data)
    return clean(list(result.txts or []))
