#!/usr/bin/env python3
"""职业库 v2 研究抓取：牛企直聘站内搜索（校招职位）→ 单岗详情页，原样缓存 HTML。

遵守 https://s.niuqizp.com/robots.txt（2026-10-05）：* 允许、Crawl-delay 4、禁止 ?Page= 翻页，
所以每个关键词只取搜索第一页（约 20 条）。标识用不含个人信息的研究 UA。可断点续跑：已缓存的不再请求。
用法：python3 crawl.py <关键词文件> [--limit N]
"""
import argparse, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "evidence" / "careerdb-2026-10-05" / "niuqi"   # evidence/ 已在 .gitignore
UA = "XiaoguResearch/0.1 (research crawl)"
DELAY = 4.0
_last = [0.0]


def get(url: str) -> str:
    # 全局限速：任意两次请求间隔不少于 Crawl-delay
    wait = DELAY - (time.time() - _last[0])
    if wait > 0:
        time.sleep(wait)
    _last[0] = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def cached(path: Path, url: str) -> str | None:
    if path.exists():
        return path.read_text(encoding="utf-8")
    try:
        html = get(url)
    except Exception as e:  # 单页失败只记录，不中断整批
        print(f"  失败 {url}: {e}", file=sys.stderr)
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return html


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords")
    ap.add_argument("--limit", type=int, default=0, help="最多抓多少个详情页（0=不限）")
    args = ap.parse_args()
    words = [w.strip() for w in Path(args.keywords).read_text(encoding="utf-8").splitlines() if w.strip() and not w.startswith("#")]
    fetched = 0
    for n, w in enumerate(words, 1):
        url = f"https://s.niuqizp.com/s_campus_{urllib.parse.quote(w)}/"
        html = cached(CACHE / "search" / f"{w}.html", url)
        if html is None:
            continue
        ids = list(dict.fromkeys(re.findall(r"//campus\.niuqizp\.com/(?:job|archivejob)-(\w+)\.html", html)))
        print(f"[{n}/{len(words)}] {w}: {len(ids)} 条", flush=True)
        for jid in ids:
            p = CACHE / "job" / f"{jid}.html"
            if p.exists():
                continue
            if args.limit and fetched >= args.limit:
                return
            if cached(p, f"https://campus.niuqizp.com/job-{jid}.html") is not None:
                fetched += 1
    print(f"完成，本次新抓详情 {fetched} 个")


if __name__ == "__main__":
    main()
