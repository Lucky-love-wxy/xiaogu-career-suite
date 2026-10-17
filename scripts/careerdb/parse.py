#!/usr/bin/env python3
"""把缓存的牛企直聘单岗详情页解析成结构化样本（只用正则读页面原有字段，不调用模型，避免抽取出错）。

输出 data/careerdb/postings.jsonl，每行一个岗位。没有“需求专业/学历要求”字段的页面（多为整份简章、图片公告）
记为 kind=brochure，不进入专业连线。
"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "evidence" / "careerdb-2026-10-05" / "niuqi" / "job"
OUT = ROOT / "data" / "careerdb" / "postings.jsonl"

def flat(raw: str) -> str:
    """去掉脚本样式后把标签换成“|”，页面上的“标签：|值”结构保留下来。"""
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S)
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", s)))
    return re.sub(r"(\s*\|\s*)+", "|", t)


def field(t: str, *labels: str) -> str | None:
    for label in labels:
        m = re.search(rf"{label}[：:]\|?([^|]{{1,200}})", t)
        if m and m.group(1).strip():
            return m.group(1).strip(" ，,;；")
    return None


def parse(jid: str, raw: str) -> dict:
    t = flat(raw)
    title = html.unescape((re.search(r"<title>(.*?)</title>", raw, re.S) or [None, ""])[1]).strip()
    m = re.match(r"(.+?)招聘(.+?)20\d\d(?:校园招聘|届)", title)
    company = m.group(1) if m else field(t, "公司名称")
    r = re.search(r'itemprop="title" content="([^"]+)"', raw)
    role = html.unescape(r.group(1)).strip() if r else (m.group(2) if m else None)
    d = re.search(r'itemprop="description">(.*?)(?:前往官网投递|免责声明)', raw, re.S)
    desc = ""
    if d:
        desc = html.unescape(re.sub(r"(\s*\n\s*)+", "\n", re.sub(r"<[^>]+>", "\n", d.group(1)))).strip()[:3000]
    majors = field(t, "招聘专业要求", "需求专业", "专业要求", "专业类别")
    rec = {
        "id": jid,
        "url": f"https://campus.niuqizp.com/job-{jid}.html",
        "title": title,
        "company": company,
        "role": role,
        "archived": "archivejob" in raw[:3000] or "|归档|" in t[:3000],
        "education": field(t, "招聘学历要求", "学历要求"),
        "majors_raw": majors,
        "category": field(t, "职位类别"),
        "headcount": field(t, "招聘人数", "人数"),
        "posted": field(t, "发布日期"),
        "city": field(t, "招聘工作地点", "工作地点"),
        "source": field(t, "来源"),
        "scale": field(t, "单位规模", "公司规模", "规模"),
        "description": desc,
    }
    rec["kind"] = "single" if role and (majors or rec["education"]) else "brochure"
    return rec


def jsonl_line(rec: dict) -> str:
    """一行一条记录。U+2028 等字符在 JSON 里合法，但 str.splitlines() 会把它当换行，下游按行读会切碎记录，所以转义。"""
    line = json.dumps(rec, ensure_ascii=False)
    for ch in "\u2028\u2029\x85\x0b\x0c\x1c\x1d\x1e":
        line = line.replace(ch, f"\\u{ord(ch):04x}")
    return line + "\n"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    n = {"single": 0, "brochure": 0}
    with OUT.open("w", encoding="utf-8") as f:
        for p in sorted(CACHE.glob("*.html")):
            rec = parse(p.stem, p.read_text(encoding="utf-8"))
            n[rec["kind"]] += 1
            f.write(jsonl_line(rec))
    print(n, "→", OUT)


if __name__ == "__main__":
    main()
