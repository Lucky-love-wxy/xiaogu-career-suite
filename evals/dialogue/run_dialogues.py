#!/usr/bin/env python3
"""对话体验回归：用本机开发服务（8781，XIAOGU_ENV=dev）的真实接口跑固定脚本，记录每轮回答。

登录走正常的邀请码 + 验证码流程：邀请码用开发口令从后台生成，验证码在 dev 环境由接口回显。
测试账号用 .test 邮箱，只存在本机开发数据库。输出 evals/dialogue/<日期>-<标签>.md 供人读。
用法：python3 evals/dialogue/run_dialogues.py <标签>
"""
import http.cookiejar, json, sys, time, urllib.request
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

SCRIPTS = {
    "1 医学生想做PM（重放 10-12 试运行）": ["你好", "我不知道该投什么岗位", "我今年上半年刚参加完大创赛，但是没有获奖，绩点也不高\n我是一名医学生，但是对于PM感兴趣",
                                      "我当时在带团队去推进一个排队算法，我主要完成算法部分，以及产品的定位方向", "互联网PM"],
    "2 打招呼后直接问岗位": ["在吗", "产品经理每天都在干啥", "那要会写代码吗"],
    "3 问黑话（含库外说法）": ["招聘上写“Owner意识”是什么意思？", "那“沉淀方法论”呢", "JD里写“能接受弹性到岗”是啥意思"],
    "4 贴 JD 再追问": ["帮我看看这个岗位：\n" + KANZHUN_JD, "我是应届生，这个能投吗", "面试的时候我该问他们什么"],
    "5 带情绪的迷茫": ["投了50份简历都没回音，好焦虑", "我是汉语言文学专业的", "其实我挺喜欢写东西的，想过做新媒体"],
}


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
    for name, turns in SCRIPTS.items():
        sid = None
        lines += [f"## {name}", ""]
        for msg in turns:
            t = time.time()
            r = post("/api/chat", {"message": msg, "session_id": sid})
            sid = r.get("session_id")
            note = f"〔标签：{r['note']}〕 " if r.get("note") else ""
            lines += [f"**用户**：{msg}", "", f"**小谷**（{r.get('status')}，{r.get('style')}，{time.time()-t:.1f}s）：{note}", "", r.get("text", "").strip(), "", "---", ""]
            print(f"[{name}] {msg[:20]} → {r.get('status')} {r.get('style')}", flush=True)
    path = OUT / f"{time.strftime('%Y-%m-%d')}-{label}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
