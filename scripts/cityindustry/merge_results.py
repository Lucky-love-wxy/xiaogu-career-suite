#!/usr/bin/env python3
"""合并 19 城 result.json → city_industry.csv（主表）+ city_industry_sources.csv（来源表）。

输入：evidence/city-industry-2026-10/{城市拼音}/result.json
输出：data/careerdb/city_industry.csv, data/careerdb/city_industry_sources.csv
"""
import json
import glob
import os
import csv

BASE = "/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch"
EV = os.path.join(BASE, "evidence/city-industry-2026-10")
OUT_MAIN = os.path.join(BASE, "data/careerdb/city_industry.csv")
OUT_SRC = os.path.join(BASE, "data/careerdb/city_industry_sources.csv")

# 城市顺序：一线4 + 新一线15（按 2025 名单顺序）
ORDER = ["北京","上海","广州","深圳",
         "成都","杭州","重庆","武汉","苏州","西安","南京","长沙","郑州","天津",
         "合肥","青岛","东莞","宁波","佛山"]

def load():
    rows = {}
    for f in sorted(glob.glob(os.path.join(EV, "*/result.json"))):
        d = json.load(open(f))
        rows[d["城市"]] = d
    return rows

def g(d, *path, default=""):
    cur = d
    for p in path:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur if cur is not None else default

def srv(rows, city, key):
    """取服务业大类某子项的值，返回 (值, 网络零售额, 来源)"""
    d = rows[city].get("服务业大类", {})
    sub = d.get(key, {})
    if not isinstance(sub, dict):
        return "", "", ""
    return (sub.get("值",""), sub.get("网络零售额",""), sub.get("来源",""))

import re

def parse_files(fp_field, sha_field):
    """解析来源的『文件路径』字段，兼容子 Agent 的复合写法。
    返回 [(文件路径, SHA256), ...]，每条对应一个真实文件。
    支持三种写法：
    1. 单路径 + 独立 SHA 字段
    2. 「路径（说明，SHA256=xxx）」—— 路径与 SHA 混在同一字段
    3. 「路径A（...）；路径B（...）」—— 一条来源多文件，用 ；分隔
    """
    if not fp_field:
        return []
    # 按全角/半角分号拆多文件
    parts = re.split(r'[；;]', fp_field)
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # 提取路径（去掉「（说明）」）
        m = re.match(r'^(\S+?)(?:（|\(|$)', part)
        path = m.group(1).strip() if m else part.strip()
        # 从说明文字里提取 SHA256
        sha = ""
        ms = re.search(r'SHA256\s*=\s*([0-9a-fA-F]{64})', part)
        if ms:
            sha = ms.group(1)
        if not path.startswith("evidence/"):
            continue
        out.append((path, sha))
    # 若没解析出 SHA，且字段本身是单一纯路径，用独立 SHA 字段兜底
    if len(out) == 1 and not out[0][1] and sha_field:
        out[0] = (out[0][0], sha_field.strip())
    return out


def main():
    rows = load()
    assert len(rows) == 19, f"期望19城，实得{len(rows)}"

    # 主表
    main_header = ["城市","城市级别","三次结构年份","一产占比%","二产占比%","三产占比%",
                   "服务业_信息软件","服务业_批零","服务业_网络零售额","服务业_金融",
                   "服务业_租赁商务","服务业_科研技术","工业重点行业","政府主导重点产业",
                   "就业结构年份","就业结构说明","电商核实","来源编号列表"]
    main_rows = []
    for city in ORDER:
        d = rows[city]
        s = d.get("三次产业结构", {})
        info = srv(rows, city, "信息软件")
        pl = srv(rows, city, "批零")
        jr = srv(rows, city, "金融")
        zl = srv(rows, city, "租赁商务")
        ky = srv(rows, city, "科研技术")
        emp = d.get("就业结构", {})
        src_ids = ",".join(x.get("来源编号","") for x in d.get("来源列表", []))
        main_rows.append([
            city, d.get("城市级别",""),
            s.get("年份",""), s.get("一产%",""), s.get("二产%",""), s.get("三产%",""),
            info[0], pl[0], pl[1], jr[0], zl[0], ky[0],
            d.get("工业重点行业",""), d.get("政府主导重点产业",""),
            emp.get("年份","") if isinstance(emp, dict) else "",
            emp.get("说明","") + (" " + emp.get("值","")) if isinstance(emp, dict) else "",
            d.get("电商核实",""),
            src_ids,
        ])

    with open(OUT_MAIN, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(main_header)
        w.writerows(main_rows)

    # 来源表
    src_header = ["来源编号","城市","来源类型","url","标题","发布方","发布日期","访问日期",
                  "文件路径","SHA256","原文短摘","证据等级","页码或条目号"]
    src_rows = []
    for city in ORDER:
        d = rows[city]
        for x in d.get("来源列表", []):
            fp = x.get("文件路径","")
            sha = x.get("SHA256","")
            files = parse_files(fp, sha)
            if not files:
                files = [("", "")]
            for i, (fpath, fsha) in enumerate(files):
                sid = x.get("来源编号","")
                if len(files) > 1:
                    sid = f"{sid}-{i+1}"
                src_rows.append([
                    sid, city, x.get("来源类型",""),
                    x.get("url",""), x.get("标题",""), x.get("发布方",""),
                    x.get("发布日期",""), x.get("访问日期",""),
                    fpath, fsha,
                    x.get("原文短摘",""), x.get("证据等级",""), x.get("页码或条目号",""),
                ])

    with open(OUT_SRC, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(src_header)
        w.writerows(src_rows)

    print(f"主表：{len(main_rows)} 城 → {OUT_MAIN}")
    print(f"来源表：{len(src_rows)} 条 → {OUT_SRC}")
    # 校验：每城都有三次结构值
    missing = [r[0] for r in main_rows if not r[2] or not r[4]]
    if missing:
        print("警告：以下城市三次结构不完整：", missing)
    else:
        print("校验通过：19 城三次结构均有年份和占比。")

if __name__ == "__main__":
    main()
