#!/usr/bin/env python3
"""对话体验回归：用本机开发服务（8781，XIAOGU_ENV=dev）的真实接口跑固定脚本，记录每轮回答。

登录走正常的邀请码 + 验证码流程：邀请码用开发口令从后台生成，验证码在 dev 环境由接口回显。
测试账号用 .test 邮箱，只存在本机开发数据库。输出 evals/dialogue/<日期>-<标签>.md 供人读。
自动检查来自用户对 round10 的逐轮标注（evals/dialogue/2026-10-13-round10.md）：每条检查注明对应哪条标注，
不通过的列在报告开头。人读仍然要做，自动检查只防已知问题回来。
用法：python3 evals/dialogue/run_dialogues.py <标签>
"""
import http.cookiejar, json, re, sys, time, urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8781"
OUT = Path(__file__).resolve().parent
KANZHUN_JD = """岗位职责：
1，负责看准用户增长产品工作，对关键指标负责
2，调研和理解用户需求，通过提炼和总结提出可行的产品/策略迭代建议，并推动落地
3，通过数据分析，发现业务问题和机会，设计AB实验，通过科学评估数据复盘总结，制定和迭代策略
4，推动跨团队协作，将策略转化为可执行、可量化的产品方案，确保项目高效落地
职位要求：
1，拥有2年以上APP产品经验，985/QS200优先考虑
2，对用户转化、流失、提频等增长关键环节有理解，结果导向
3，有Owner意识和执行力，能高效推动跨团队协作并拿到业务结果
岗位亮点：重点孵化产品，百人团队，业务高速发展，能沉淀方法论，机会多空间大"""

CARD_DONE = "我填好了基本情况，帮我看看能往哪些方向走"
CARD_LIT = {"学历": "本科", "专业": "汉语言文学", "毕业时间": "2026届", "意向城市": "杭州", "城市偏好": ["新一线"],
            "单位类型": ["中小公司", "初创公司"], "期望月薪": "5千-8千", "经历": "在校报社做了两年编辑，写过二十多篇稿子；运营过学院公众号，没有公司实习"}

# 每个脚本：轮次列表；可选 card（这个脚本开始前把基本情况卡片设成它，没有就清空）
SCRIPTS = {
    "1 医学生想做PM（重放 10-12 试运行）": ["你好", "我不知道该投什么岗位", "我今年上半年刚参加完大创赛，但是没有获奖，绩点也不高\n我是一名医学生，但是对于PM感兴趣",
                                      "我当时在带团队去推进一个排队算法，我主要完成算法部分，以及产品的定位方向", "互联网PM"],
    "2 打招呼后直接问岗位": ["在吗", "产品经理每天都在干啥", "那要会写代码吗"],
    "3 问黑话（含库外说法）": ["招聘上写“Owner意识”是什么意思？", "那“沉淀方法论”呢", "JD里写“能接受弹性到岗”是啥意思"],
    "4 贴 JD 再追问": ["帮我看看这个岗位：\n" + KANZHUN_JD, "我是应届生，这个能投吗", "面试的时候我该问他们什么"],
    "5 带情绪的迷茫": ["投了50份简历都没回音，好焦虑", "我是汉语言文学专业的", "其实我挺喜欢写东西的，想过做新媒体"],
    "6 填好基本情况后要方向": {"card": CARD_LIT, "turns": [CARD_DONE, "第一个具体每天做什么"]},
    "7 不填卡、在聊天里说清情况": ["我是汉语言文学专业的，26届，不知道该投什么岗位", "我更想留在杭州"],
}

# 单轮检查：(脚本名, 第几轮从 0 数, 检查名, 函数, 对应标注)
TURN_CHECKS = [
    ("1 医学生想做PM（重放 10-12 试运行）", 0, "开场白不提模拟面试和面试复盘", lambda r: not re.search(r"模拟面试|面试复盘", r["text"]), "第 2 段第 1 轮"),
    ("2 打招呼后直接问岗位", 0, "开场白不提模拟面试和面试复盘", lambda r: not re.search(r"模拟面试|面试复盘", r["text"]), "第 2 段第 1 轮"),
    ("2 打招呼后直接问岗位", 0, "开场白只问一个问题", lambda r: r["text"].count("？") + r["text"].count("?") <= 1, "round13 人工发现"),
    ("1 医学生想做PM（重放 10-12 试运行）", 1, "没填卡时先请用户填卡，不急着给方向", lambda r: r.get("action") == "profile_card" and not re.search(r"(?m)^1\. ", r["text"]), "第 1 段第 2、4 轮"),
    ("3 问黑话（含库外说法）", 2, "教了怎么问，也说了对方不正面回答怎么办", lambda r: bool(re.search(r"面聊|不正面|回避|含糊|不回答|不愿意说", r["text"])), "第 3 段第 3 轮"),
    ("6 填好基本情况后要方向", 0, "提交卡片后直接给候选，且引用卡片内容", lambda r: bool(re.search(r"(?m)^1\. ", r["text"])) and bool(re.search(r"校报|公众号|汉语言|杭州", r["text"])), "第 1 段第 4 轮"),
    ("6 填好基本情况后要方向", 0, "候选不复述期望月薪数字", lambda r: not re.search(r"5千|8千|\d+[kK]", r["text"]), "期望月薪只理解偏好"),
    ("7 不填卡、在聊天里说清情况", 0, "聊天里已说清专业和届别，不再请填卡，直接给候选", lambda r: r.get("action") != "profile_card" and bool(re.search(r"(?m)^1\. ", r["text"])), "第 1 段第 4 轮"),
]


def global_failures(r):
    """每轮都查：结尾不带句号；聊天回答不出现超长段落（第 1 段第 3 轮：一大段没排版）。"""
    text, out = (r.get("text") or "").strip(), []
    if text.endswith("。"):
        out.append("结尾带了句号（第 2 段第 1 轮）")
    if r.get("style") == "chat":
        long = [p for p in re.split(r"\n\s*\n", text) if not re.match(r"^\d+\. |^- ", p) and len(p) > 160]
        if long:
            out.append(f"有 {len(long)} 段超过 160 字（第 1 段第 3 轮）")
    return out


def client():
    jar = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    def post(path, body):
        req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with op.open(req, timeout=180) as r:
            return json.load(r)
    return post


def login(post):
    post("/api/admin/login", {"token": "dev-admin"})
    invite = post("/api/admin/invites", {"count": 1, "credits": 3000, "note": "对话回归测试"})["codes"][0]
    contact = f"dialogue-eval-{int(time.time())}@xiaogu.test"
    code = post("/api/auth/code", {"contact": contact})["dev_code"]
    post("/api/auth/verify", {"contact": contact, "code": code, "invite": invite, "consent": True})
    return contact


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    post = client()
    contact = login(post)
    lines = [f"# 对话回归 · {label}", "", f"- 时间：{time.strftime('%Y-%m-%d %H:%M')}；服务：{BASE}；测试账号：{contact}", ""]
    failures, checked = [], 0
    for name, spec in SCRIPTS.items():
        turns, card = (spec["turns"], spec.get("card")) if isinstance(spec, dict) else (spec, None)
        post("/api/me/profile", {"profile": card or {}})  # 卡片按用户存：每个脚本开始前设好或清空
        sid, card_asks = None, 0
        lines += [f"## {name}", ""] + ([f"（本段开始前已填基本情况卡片：{json.dumps(card, ensure_ascii=False)}）", ""] if card else [])
        for i, msg in enumerate(turns):
            t = time.time()
            r = post("/api/chat", {"message": msg, "session_id": sid})
            sid = r.get("session_id")
            note = f"〔标签：{r['note']}〕 " if r.get("note") else ""
            action = f"〔按钮：{r['action']}〕 " if r.get("action") else ""
            bad = [f"{name} 第 {i + 1} 轮：{f}" for f in global_failures(r)]
            card_asks += r.get("status") == "needs_input" and r.get("action") == "profile_card"
            if card_asks > 1:
                bad.append(f"{name} 第 {i + 1} 轮：同一对话第 {card_asks} 次请填卡（round13 人工发现）")
            for script, turn, title, check, source in TURN_CHECKS:
                if script == name and turn == i:
                    checked += 1
                    if not check(r):
                        bad.append(f"{name} 第 {i + 1} 轮：{title}（{source}）")
            failures += bad
            lines += [f"**用户**：{msg}", "", f"**小谷**（{r.get('status')}，{r.get('style')}，{time.time()-t:.1f}s）：{note}{action}", "",
                      r.get("text", "").strip(), ""] + ([f"> 自动检查未通过：{'；'.join(b.split('：', 1)[1] for b in bad)}", ""] if bad else []) + ["---", ""]
            print(f"[{name}] {msg[:20]} → {r.get('status')} {r.get('style')}{' ✗' if bad else ''}", flush=True)
    post("/api/me/profile", {"profile": {}})
    summary = [f"## 自动检查：{'全部通过' if not failures else f'{len(failures)} 处未通过'}（单轮检查 {checked} 项 + 每轮的全局检查）", ""]
    summary += [f"- {f}" for f in failures] + [""]
    lines[4:4] = summary
    path = OUT / f"{time.strftime('%Y-%m-%d')}-{label}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(path)
    print("\n".join(summary))


if __name__ == "__main__":
    main()
