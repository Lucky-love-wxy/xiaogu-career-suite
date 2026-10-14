"""基本情况：卡片一次填完（notes/2026-10-14-基本情况卡片与对话标注修复.md），代码记哪些已知、问过的和已知的不再问。
10-13 的逐项提问（notes/2026-10-13-画像提问.md）已由卡片取代，这里只留仍然有效的规则。"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT / "tests"))
import agent  # noqa: E402
from test_web_agent import JD, ScriptedProvider  # noqa: E402

CARD = {"学校": "某某大学", "学历": "本科", "专业": "汉语言文学", "毕业时间": "2026届", "城市偏好": ["新一线"],
        "单位类型": ["中小公司"], "期望月薪": "5千-8千", "经历": "在校报社写过 20 篇稿子"}


def chat_out(next_action, facts=None, candidates=None):
    body = {"answer": "挺好的，先说说我的看法。", "evidence_ids": [], "inferences": [], "unknown": [],
            "next_action": next_action, "facts": facts or {}}
    if candidates:
        body["candidates"] = candidates
    return json.dumps(body, ensure_ascii=False)


CANDS = [{"role": "新媒体编辑", "reason": "在校报社写过稿"}, {"role": "内容运营", "reason": "文字功底"}]


class CardRulesTests(unittest.TestCase):
    def test_clean_card_keeps_only_known_fields_and_choices(self):
        out = agent.clean_card({"专业": "  汉语言文学 ", "学历": "小学", "城市偏好": ["一线", "火星"], "期望月薪": "5千-8千",
                                "经历": "写" * 2000, "身份证号": "110"})
        self.assertEqual(out["专业"], "汉语言文学")
        self.assertNotIn("学历", out)  # 不在可选值里
        self.assertEqual(out["城市偏好"], ["一线"])
        self.assertEqual(len(out["经历"]), 1500)
        self.assertNotIn("身份证号", out)
        self.assertEqual(agent.clean_card({"专业": " "}), {})

    def test_card_ready_from_card_facts_or_this_message(self):
        s = agent.Session()
        self.assertFalse(agent.card_ready(s))
        token = agent.CARD.set({"专业": "统计学", "毕业时间": "2026届"})
        try:
            self.assertTrue(agent.card_ready(s))
        finally:
            agent.CARD.reset(token)
        s.facts.update({"专业": "统计学", "年级": "大三"})
        self.assertTrue(agent.card_ready(s))
        # 不填卡、这一轮原话里说清了，也不挡
        self.assertTrue(agent.card_ready(agent.Session(), "我是汉语言文学专业的，26届，不知道投什么"))

    def test_fresh_graduate_is_not_a_degree(self):
        # 模型把“应届生”写进学历：不能当成知道了学历
        self.assertFalse(agent.profile_known(agent.Session(facts={"学历": "应届生"}), "学历"))

    def test_card_hint_only_without_card_and_only_once(self):
        s = agent.Session()
        self.assertEqual(agent.profile_gap("general", s, False), "卡片")
        for task in ("propose", "jargon", "jargon_unlisted", "resume", "interview"):
            self.assertIsNone(agent.profile_gap(task, s, False), task)
        s.profile_asked.append("卡片")
        self.assertIsNone(agent.profile_gap("general", s, False))
        token = agent.CARD.set(CARD)
        try:
            self.assertIsNone(agent.profile_gap("general", agent.Session(), False))
        finally:
            agent.CARD.reset(token)


class CardFlowTests(unittest.TestCase):
    def test_direction_without_card_asks_for_card_with_action(self):
        a = agent.Agent(ScriptedProvider([], intent="direction", role=None))
        result = a.handle(None, "我不知道该投什么岗位")
        self.assertEqual(result["status"], "needs_input")
        self.assertEqual(result["action"], "profile_card")
        self.assertIn("基本情况", result["text"])

    def test_never_filling_the_card_does_not_loop(self):
        # 同一句“先填卡”不连发两次：第二次交给模型按上下文接话（repeat_guard）
        p = ScriptedProvider([chat_out("你最近有在看哪类岗位吗？")], intent="direction", role=None)
        a = agent.Agent(p)
        first = a.handle(None, "我不知道该投什么岗位")
        second = a.handle(first["session_id"], "就是不知道")
        self.assertTrue(second["trace"].get("repeat_guard"))
        self.assertEqual(second["status"], "complete")

    def test_card_done_goes_straight_to_candidates(self):
        # 分类器即使判成打招呼，提交卡片那句也直接给候选
        p = ScriptedProvider([chat_out("你想先了解哪一个？", candidates=CANDS)], intent="greeting", role=None)
        a = agent.Agent(p)
        result = a.handle(None, agent.CARD_DONE, card=CARD)
        self.assertEqual(result["trace"]["route"]["task"], "propose")
        self.assertEqual(p.classified, 0)
        self.assertIn("1. 新媒体编辑", result["text"])
        self.assertIn("汉语言文学", p.prompts[0])  # 卡片内容进了提示词
        self.assertIn("期望月薪只用来理解偏好", p.prompts[0])

    def test_card_ready_first_direction_proposes_once(self):
        p = ScriptedProvider([chat_out("你想先了解哪一个？", candidates=CANDS), chat_out("你更看重哪一点？")],
                             intent="direction", role=None)
        a = agent.Agent(p)
        first = a.handle(None, "我不知道该投什么", card=CARD)
        self.assertEqual(first["trace"]["route"]["task"], "propose")
        # 已经给过一批（候选已被挑走）：再进找方向按原来的聊天接话，不会每轮都另起一批
        a.sessions[first["session_id"]].candidates = []
        second = a.handle(first["session_id"], "还是有点拿不准", card=CARD)
        self.assertEqual(second["trace"]["route"]["task"], "direction")

    def test_card_is_not_copied_into_session_state(self):
        import dataclasses
        p = ScriptedProvider([chat_out("你想先了解哪一个？", candidates=CANDS)], intent="direction", role=None)
        a = agent.Agent(p)
        sid = a.handle(None, agent.CARD_DONE, card=CARD)["session_id"]
        state = json.dumps(dataclasses.asdict(a.sessions[sid]), ensure_ascii=False)
        self.assertNotIn("在校报社写过 20 篇稿子", state)
        self.assertIsNone(agent.CARD.get())  # 请求结束后上下文清掉

    def test_card_hint_turns_into_button(self):
        p = ScriptedProvider([chat_out("方便的话点左边的「+」填一下基本情况，我能更准地帮你判断")], intent="general_advice", role=None)
        result = agent.Agent(p).handle(None, "群面一般怎么准备")
        self.assertIn("用户还没填「基本情况」卡片", p.prompts[0])
        self.assertEqual(result["action"], "profile_card")
        self.assertEqual(result["trace"]["profile_asked"], "卡片")


class RepeatGuardTests(unittest.TestCase):
    def test_asking_what_the_card_already_says_is_rewritten(self):
        p = ScriptedProvider([chat_out("你是哪一届毕业的？"), chat_out("你更想先弄清楚哪件事？")], intent="general_advice", role=None)
        result = agent.Agent(p).handle(None, "我现在该干嘛", card=CARD)
        self.assertEqual(p.calls, 2)
        self.assertIn("又在问用户的「毕业时间」", result["trace"]["attempts"][0][0])

    def test_asking_what_the_user_just_said_is_rewritten(self):
        p = ScriptedProvider([chat_out("你是哪一届毕业的？", {"毕业时间": "应届生"}), chat_out("你更想先弄清楚哪件事？")],
                             intent="general_advice", role=None)
        result = agent.Agent(p).handle(None, "我是应届生，现在该干嘛")
        self.assertIn("又在问用户的「毕业时间」", result["trace"]["attempts"][0][0])
        self.assertIn("哪件事", result["text"])

    def test_last_question_is_named_and_repeats_are_rewritten(self):
        ask = "你手上还有这个岗位的完整招聘说明吗？发我看看，我帮你把里面其他话术也一起拆一下。"
        p = ScriptedProvider([chat_out(ask), chat_out("你手上这个岗位的招聘说明还在吗？发我看看，我帮你把里面其他话术也一起拆一下。"),
                              chat_out("你最近在看哪一类岗位？")], intent="general_advice", role=None)
        a = agent.Agent(p)
        first = a.handle(None, "群面一般怎么准备", card=CARD)
        second = a.handle(first["session_id"], "那无领导小组讨论呢", card=CARD)
        self.assertIn(f"上一轮你最后对用户说的是：“{ask}”", p.prompts[1])
        self.assertIn("几乎一样", second["trace"]["attempts"][0][0])
        self.assertIn("哪一类岗位", second["text"])


class EndingTests(unittest.TestCase):
    def test_reply_never_ends_with_a_full_stop(self):
        out = json.dumps({"answer": "先别急，慢慢来。", "evidence_ids": [], "next_action": None}, ensure_ascii=False)
        result = agent.Agent(ScriptedProvider([out], intent="general_advice", role=None)).handle(None, "好焦虑", card=CARD)
        self.assertFalse(result["text"].endswith("。"))

    def test_pasted_jd_report_still_works_without_card(self):
        result = agent.Agent(agent.MockProvider()).handle(None, "帮我看看这个岗位：\n" + JD)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["trace"].get("profile_gap"), "卡片")


if __name__ == "__main__":
    unittest.main()
