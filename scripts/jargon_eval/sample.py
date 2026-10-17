#!/usr/bin/env python3
"""黑话覆盖率评测的抽样（固定随机种子，可复现）。

校招 50 份：从牛企直聘已抓的单岗页里分层随机抽，每家公司最多 1 份（避免同一家公司的写法占比过高），
按岗位大类轮流抽（每类先 1 份，再一轮轮补）：库是按医学方向抓的，按比例分配会让医疗类占七成，轮流抽保证各行业都覆盖。社招 50 份：生成“抽签单”，由用户照单去招聘网站取 JD，避免只截自己感兴趣的岗位。
两部分各自再随机对半分成 tune（可以据此补词条）和 holdout（只用来算覆盖率，不许据此改库）。
"""
import json, random
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "jargon_eval"
SEED = 20261012
N = 50


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").split("\n") if l.strip()]


def campus(rng):
    posts = {r["url"]: r for r in jl(ROOT / "data/careerdb/postings.jsonl") if r["kind"] == "single"}
    mapped = {r["url"]: r for r in jl(ROOT / "data/careerdb/postings_mapped.jsonl")}
    strata, seen = defaultdict(list), set()
    pool = [u for u in posts if len(posts[u].get("description") or "") >= 150]  # 正文太短的没有话术可标
    rng.shuffle(pool)
    for u in pool:
        company = posts[u].get("company")
        if company in seen:
            continue
        seen.add(company)
        node = (mapped.get(u) or {}).get("node") or "未归类"
        strata[node.split(" › ")[0]].append(u)
    alloc, keys = defaultdict(int), sorted(strata, key=lambda k: rng.random())
    while sum(alloc.values()) < N and any(alloc[k] < len(strata[k]) for k in keys):
        for k in keys:  # 轮流：每一轮每个大类最多再拿 1 份
            if sum(alloc.values()) < N and alloc[k] < len(strata[k]):
                alloc[k] += 1
    picked = [(k, u) for k, n in alloc.items() for u in strata[k][:n]]
    rng.shuffle(picked)
    rows = [{"id": f"campus-{i:03d}", "stratum": k, "url": u, "company": posts[u]["company"], "role": posts[u]["role"],
             "text": posts[u]["description"], "split": "tune" if i % 2 else "holdout"} for i, (k, u) in enumerate(picked, 1)]
    return rows, {k: (len(v), alloc[k]) for k, v in strata.items()}


def social_draws(rng):
    top = json.loads((ROOT / "evidence/careerdb-2026-10-05/boss-position-tree.json").read_text(encoding="utf-8"))["zpData"]["position"]
    cats = [t for t in top if t["name"] not in ("其他", "技工/普工")]  # 普工类不是大学生求职目标
    cities = ["北京", "上海", "深圳", "杭州", "广州", "成都", "武汉", "南京"]
    draws = []
    for i in range(1, N + 1):
        a = rng.choice(cats)  # 先等概率抽大类，避免互联网类岗位淹没其他行业
        b = rng.choice(a["subLevelModelList"])
        c = rng.choice(b["subLevelModelList"])
        draws.append({"id": f"social-{i:03d}", "category": f"{a['name']} › {b['name']}", "keyword": c["name"],
                      "city": rng.choice(cities), "rank": rng.randint(1, 10), "split": "tune" if i % 2 else "holdout"})
    return draws


def main():
    rng = random.Random(SEED)
    rows, strata = campus(rng)
    draws = social_draws(rng)
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "campus_sample.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT / "social_draws.json").write_text(json.dumps(draws, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = ["# 社招 JD 抽签单（50 份）", "",
             f"随机种子 {SEED}，由 scripts/jargon_eval/sample.py 生成。请按顺序取，不要跳过不感兴趣的。", "",
             "取法：在招聘网站（BOSS 直聘网页或 App 均可）搜索【搜索词】，城市选该组的城市，经验筛选选“1-3年”；"
             "从结果列表第【名次】条打开，复制或截图完整职位描述（职责 + 要求）。", "",
             "- 第【名次】条是校招、实习或兼职 → 往下顺延到第一条社招全职。",
             "- 结果不足【名次】条 → 取最后一条社招；一条社招都没有 → 在表里记“无结果”，换下一行，不要自己换词。",
             "- 同一家公司已经取过 → 顺延到下一条。", "",
             "按城市分组，方便切换一次城市后连续取完；编号保持不变。", ""]
    by_city = {}
    for d in draws:
        by_city.setdefault(d["city"], []).append(d)
    for city, ds in sorted(by_city.items(), key=lambda kv: -len(kv[1])):
        lines += [f"## {city}（{len(ds)} 份）", "", "| 编号 | 大类 › 中类 | 搜索词 | 名次 | 已取 |", "|---|---|---|---:|---|"]
        lines += [f"| {d['id']} | {d['category']} | {d['keyword']} | {d['rank']} | □ |" for d in ds]
        lines.append("")
    (OUT / "social_draws.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("校招分层（大类：可抽数 → 名额）：", {k: v for k, v in sorted(strata.items(), key=lambda kv: -kv[1][0])})
    print("校招", len(rows), "份；社招抽签", len(draws), "条")


if __name__ == "__main__":
    main()
