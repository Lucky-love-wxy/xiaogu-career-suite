"""画像提问（notes/2026-10-13-画像提问.md）：代码记哪些基础信息还缺、这一轮只提示一项、问过不再提示。"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT / "tests"))
import agent  # noqa: E402
from test_web_agent import JD, ScriptedProvider  # noqa: E402


def chat_out(next_action, facts=None):
    return json.dumps({"answer": "挺好的，先说说我的看法。", "evidence_ids": [], "inferences": [], "unknown": [],
                       "next_action": next_action, "facts": facts or {}}, ensure_ascii=False)


class ProfileGapTests(unittest.TestCase):
    def test_picks_first_missing_slot_for_the_task(self):
        s = agent.Session()
        self.assertEqual(agent.profile_gap("direction", s, False), "专业")
        s.facts["专业"] = "临床医学"
        self.assertEqual(agent.profile_gap("direction", s, False), "毕业时间")
        # 模型写的键名不统一：“年级: 大三”也算知道了毕业时间
        s.facts["年级"] = "大三"
        self.assertEqual(agent.profile_gap("direction", s, False), "经历")

    def test_jd_tasks_ask_what_decides_eligibility_first(self):
        s = agent.Session()
        self.assertEqual(agent.profile_gap("suite", s, True), "毕业时间")
        self.assertEqual(agent.profile_gap("jd_followup", s, True), "毕业时间")
        s.facts["学校"] = "某某大学 本科"  # 学历藏在别的键的值里也算知道
        s.facts["毕业"] = "2026届"
        self.assertEqual(agent.profile_gap("suite", s, True), "专业")
        # 没贴 JD 的岗位问答只问专业、毕业时间：两项都知道了就不再提示
        s.facts["专业"] = "统计学"
        self.assertIsNone(agent.profile_gap("suite", s, False))

    def test_stored_experience_counts(self):
        s = agent.Session(experience="我做过一个课程推荐项目")
        s.facts.update({"专业": "统计学", "毕业时间": "2026届"})
        self.assertEqual(agent.profile_gap("direction", s, False), "意向城市")

    def test_tasks_with_their_own_question_are_left_alone(self):
        s = agent.Session()
        for task in ("propose", "jargon", "jargon_unlisted", "resume", "interview"):
            self.assertIsNone(agent.profile_gap(task, s, True), task)

    def test_fresh_graduate_is_not_a_degree(self):
        # 模型把“应届生”写进学历：不能当成知道了学历；“应届”本身算知道毕业时间
        s = agent.Session(facts={"学历": "应届生"})
        self.assertEqual(agent.profile_gap("suite", s, True), "学历")

    def test_cooldown_after_asking(self):
        s = agent.Session(profile_asked=["专业"], profile_asked_turn=3, turns=4)
        self.assertIsNone(agent.profile_gap("direction", s, False))
        s.turns = 5
        self.assertEqual(agent.profile_gap("direction", s, False), "毕业时间")

    def test_asked_slot_is_not_offered_again(self):
        s = agent.Session(profile_asked=["专业"])
        self.assertEqual(agent.profile_gap("direction", s, False), "毕业时间")


class ProfileFlowTests(unittest.TestCase):
    def test_gap_is_offered_then_marked_asked(self):
        p = ScriptedProvider([chat_out("你现在读的是什么专业呀？"), chat_out("你是哪一届毕业？", {"专业": "汉语言文学"})],
                             intent="direction", role=None)
        a = agent.Agent(p)
        first = a.handle(None, "我不知道该找什么工作")
        self.assertIn("小谷还不知道用户的「专业」", p.prompts[0])
        self.assertEqual(first["trace"]["profile_asked"], "专业")
        second = a.handle(first["session_id"], "我学汉语言文学的")
        # 上一轮刚问过：这一轮不提示，先聊用户的话
        self.assertNotIn("小谷还不知道用户", p.prompts[1])
        self.assertNotIn("profile_gap", second["trace"])
        p.outputs.append(chat_out(None))
        p.intent = "general_advice"  # 第 3 轮的找方向会强制出候选（PROPOSE_AFTER），那个任务不提示画像；这里换成一般问答
        third = a.handle(first["session_id"], "群面一般怎么准备")
        # 隔一轮：专业已知、也问过，换成毕业时间
        self.assertIn("「毕业时间」", p.prompts[2])
        self.assertEqual(third["trace"]["profile_gap"], "毕业时间")

    def test_unasked_gap_stays_open(self):
        # 模型判断时机不自然、没问：下一轮仍然可以提示同一项，但不强制
        p = ScriptedProvider([chat_out("你最近有没有特别想试的方向？"), chat_out(None)], intent="direction", role=None)
        a = agent.Agent(p)
        first = a.handle(None, "我好迷茫")
        self.assertNotIn("profile_asked", first["trace"])
        a.handle(first["session_id"], "就是不知道干嘛")
        self.assertIn("「专业」", p.prompts[1])

    def test_reasking_a_known_or_asked_slot_is_rewritten(self):
        # 用户说了“应届生”，模型还问“哪一届”：判不通过，重写后换成别的问题
        p = ScriptedProvider([chat_out("你是哪一届毕业的？", {"毕业时间": "应届生"}), chat_out("你更想先弄清楚哪件事？")],
                             intent="general_advice", role=None)
        a = agent.Agent(p)
        result = a.handle(None, "我是应届生，现在该干嘛")
        self.assertEqual(p.calls, 2)
        self.assertIn("又在问用户的「毕业时间」", result["trace"]["attempts"][0][0])
        self.assertIn("哪件事", result["text"])

    def test_pasted_jd_offers_graduation_year(self):
        a = agent.Agent(agent.MockProvider())
        result = a.handle(None, "帮我看看这个岗位：\n" + JD)
        self.assertEqual(result["trace"].get("profile_gap"), "毕业时间")


if __name__ == "__main__":
    unittest.main()
