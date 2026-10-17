"""XMind 导出公共件：黑底白线主题 + 写 .xmind 文件。

用户 2026-10-07 定的默认风格：所有层级图一律黑底、白色连线、白字、无彩色分支。
主题字段照抄 Xmind.app 内置主题的结构（map / centralTopic / mainTopic / subTopic …），只改颜色。
"""
import json
import uuid
import zipfile

WHITE, BLACK, GREY = "#FFFFFF", "#000000", "#BFBFBF"


def _topic_style(size, weight, border):
    return {"id": uuid.uuid4().hex, "properties": {
        "fo:font-size": size, "fo:font-weight": weight, "fo:color": WHITE,
        "svg:fill": BLACK, "fill-pattern": "solid",
        "line-color": WHITE, "line-width": "1.5pt", "line-pattern": "solid",
        "border-line-color": WHITE, "border-line-width": border,
        "shape-class": "org.xmind.topicShape.roundedRect",
        "line-class": "org.xmind.branchConnection.roundedElbow",
    }}


def dark_theme():
    # multi-line-colors=none 关掉彩虹分支色，连线统一用 line-color 白色
    return {
        "map": {"id": uuid.uuid4().hex, "properties": {
            "svg:fill": BLACK, "multi-line-colors": "none", "color-list": WHITE, "line-tapered": "none"}},
        "centralTopic": _topic_style("24pt", "700", "2pt"),
        "mainTopic": _topic_style("16pt", "600", "1pt"),
        "subTopic": _topic_style("13pt", "400", "0pt"),
        "floatingTopic": _topic_style("13pt", "400", "1pt"),
        "summaryTopic": _topic_style("13pt", "400", "1pt"),
        "calloutTopic": _topic_style("13pt", "400", "1pt"),
        "boundary": {"id": uuid.uuid4().hex, "properties": {
            "svg:fill": BLACK, "line-color": GREY, "fo:color": WHITE}},
        "summary": {"id": uuid.uuid4().hex, "properties": {"line-color": WHITE}},
        "relationship": {"id": uuid.uuid4().hex, "properties": {"line-color": GREY, "fo:color": WHITE}},
    }


def apply_dark(sheets):
    """给每个画布挂上黑底主题（会覆盖原有 theme）。"""
    for s in sheets:
        s["theme"] = dark_theme()
    return sheets


def upsert_sheets(sheets, path, creator="xiaogu-export"):
    """项目只维护一个 XMind：按画布标题替换同名画布，新标题追加到末尾，其他画布原样保留。"""
    from pathlib import Path
    old = []
    if Path(path).exists():
        with zipfile.ZipFile(path) as z:
            old = json.loads(z.read("content.json"))
    new_by_title = {s["title"]: s for s in sheets}
    merged = [new_by_title.pop(s["title"], s) for s in old] + list(new_by_title.values())
    write_xmind(merged, path, creator)
    return [s["title"] for s in merged]


def write_xmind(sheets, path, creator="xiaogu-export"):
    apply_dark(sheets)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.json", json.dumps(sheets, ensure_ascii=False))
        z.writestr("metadata.json", json.dumps({"creator": {"name": creator, "version": "1"}}))
        z.writestr("manifest.json", json.dumps({"file-entries": {"content.json": {}, "metadata.json": {}}}))
