"""用户记忆文档（notes/2026-10-14-用户记忆文档.md）：跨对话记住情况、方向批次和反馈；清理（方案 A）；对话满 12 轮压缩上下文。"""

import dataclasses
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT / "tests"))
import agent  # noqa: E402
from test_profile import CARD, CANDS, chat_out  # noqa: E402
from test_web_agent import JD, ScriptedProvider  # noqa: E402


def out(next_action="你想先了解哪一个？", **extra):
    body = json.loads(chat_out(next_action))
    body.update(extra)
    return json.dumps(body, ensure_ascii=False)


class MemoryWriteTests(unittest.TestCase):
    def test_batch_pick_and_feedback_are_recorded(self):
        memory = {}
        p = ScriptedProvider([out(candidates=CANDS),
                              out("你更在意哪一点？", feedback=[{"kind": "不喜欢", "detail": "内容运营：太累"},
                                                               {"kind": "瞎编的类", "detail": "不收"}])],
                             intent="direction", role=None)
        a = agent.Agent(p)
        first = a.handle(None, agent.CARD_DONE, card=CARD, memory=memory)
        self.assertEqual(memory["batches"][0]["directions"], ["新媒体编辑", "内容运营", "编辑助理"])
        p.intent = "general_advice"
        a.handle(first["session_id"], "内容运营我不太想做，太累了", card=CARD, memory=memory)
        kinds = [f["kind"] for f in memory["feedback"]]
        self.assertEqual(kinds, ["不喜欢"])  # 不在枚举里的类别不收

    def test_pick_and_pasted_jd_are_recorded_by_code(self):
        memory = {}
        a = agent.Agent(ScriptedProvider([out(candidates=CANDS), out(None)], intent="direction", role=None))
        sid = a.handle(None, agent.CARD_DONE, card=CARD, memory=memory)["session_id"]
        a.handle(sid, "第二个", card=CARD, memory=memory)
        self.assertEqual(memory["feedback"][0], {**memory["feedback"][0], "kind": "选了方向", "detail": "内容运营"})
        agent.Agent(agent.MockProvider()).handle(None, "帮我看看这个岗位：\n" + JD, memory=memory)
        self.assertEqual(memory["feedback"][-1]["kind"], "看了招聘说明")

    def test_rejection_mentioning_a_candidate_is_not_a_pick(self):
        self.assertIsNone(agent.pick_candidate("内容运营我不太想做，太累了", ["新媒体编辑", "内容运营"]))
        self.assertIsNone(agent.pick_candidate("第二个算了", ["新媒体编辑", "内容运营"]))
        self.assertEqual(agent.pick_candidate("第二个", ["新媒体编辑", "内容运营"]), "内容运营")
        self.assertEqual(agent.pick_candidate("内容运营", ["新媒体编辑", "内容运营"]), "内容运营")

    def test_changed_fact_keeps_previous_value(self):
        memory = {}
        p = ScriptedProvider([out(None, facts={"意向城市": "杭州"}), out(None, facts={"意向城市": "上海"})], intent="general_advice", role=None)
        a = agent.Agent(p)
        sid = a.handle(None, "我想去杭州", memory=memory)["session_id"]
        a.handle(sid, "算了还是上海吧", memory=memory)
        self.assertEqual(memory["facts"]["意向城市"]["value"], "上海")
        self.assertEqual(memory["facts"]["意向城市"]["previous"][0]["value"], "杭州")

    def test_without_memory_argument_nothing_is_written(self):
        a = agent.Agent(ScriptedProvider([out(candidates=CANDS)], intent="direction", role=None))
        a.handle(None, agent.CARD_DONE, card=CARD)  # 不传 memory：老调用方式照常工作
        self.assertIsNone(agent.MEMORY.get())


class MemoryReadTests(unittest.TestCase):
    def test_new_conversation_sees_last_batches_and_feedback(self):
        memory = {}
        p = ScriptedProvider([out(candidates=CANDS), out(None), out("你想先了解哪一个？", candidates=CANDS)], intent="direction", role=None)
        a = agent.Agent(p)
        sid = a.handle(None, agent.CARD_DONE, card=CARD, memory=memory)["session_id"]
        a.handle(sid, "第一个", card=CARD, memory=memory)
        # 另开一个对话：提示词里有上一批方向和“选了方向”的反馈
        a.handle(None, "上次那几个我看完了，再给我一批", card=CARD, memory=memory)
        prompt = p.prompts[-1]
        self.assertIn("<memory>", prompt)
        self.assertIn("新媒体编辑、内容运营、编辑助理", prompt)
        self.assertIn("选了方向：新媒体编辑", prompt)
        self.assertEqual(len(memory["batches"]), 2)

    def test_next_batch_in_new_conversation_is_propose_not_job_search(self):
        memory = {"batches": [{"at": "10-14", "t": 1, "directions": ["新媒体编辑", "内容运营", "编辑助理"]}]}
        p = ScriptedProvider([out("你想先了解哪一个？", candidates=CANDS)], intent="job_search", role=None)
        result = agent.Agent(p).handle(None, "上次那几个方向我想了想，再给我一批", card=CARD, memory=memory)
        self.assertEqual(result["trace"]["route"]["task"], "propose")
        self.assertEqual(p.classified, 0)
        self.assertEqual(len(memory["batches"]), 2)

    def test_only_recent_three_batches_go_into_prompt(self):
        mem = {"batches": [{"at": f"10-0{i}", "t": i, "directions": [f"方向{i}"]} for i in range(1, 6)]}
        text = agent.memory_text(mem)
        self.assertNotIn("方向1", text)
        self.assertNotIn("方向2", text)
        self.assertIn("方向5", text)

    def test_remembered_fact_is_not_asked_again(self):
        memory = {"facts": {"毕业时间": {"value": "2026届", "at": "10-13"}}}
        p = ScriptedProvider([out("你是哪一届毕业的？"), out("你更想先弄清楚哪件事？")], intent="general_advice", role=None)
        result = agent.Agent(p).handle(None, "我现在该干嘛", memory=memory)
        self.assertIn("又在问用户的「毕业时间」", result["trace"]["attempts"][0][0])


class CleanMemoryTests(unittest.TestCase):
    def test_compress_keeps_recent_three_and_summarizes_older(self):
        mem = {"batches": [{"at": f"10-0{i}", "t": i, "directions": [f"方向{i}"]} for i in range(1, 6)],
               "feedback": [{"at": "10-01", "t": 1.5, "kind": "不喜欢", "detail": "方向1"},
                            {"at": "10-05", "t": 5.5, "kind": "选了方向", "detail": "方向5"}],
               "facts": {"意向城市": {"value": "上海", "at": "10-05", "previous": [{"value": "杭州", "at": "10-01"}]}}}
        merged, dropped = agent.compress_memory(mem)
        self.assertEqual((merged, dropped), (2, 1))
        self.assertEqual([b["directions"][0] for b in mem["batches"]], ["方向3", "方向4", "方向5"])
        self.assertIn("方向1", mem["summary"])
        self.assertIn("不喜欢：方向1", mem["summary"])
        self.assertEqual([f["detail"] for f in mem["feedback"]], ["方向5"])
        self.assertNotIn("previous", mem["facts"]["意向城市"])

    def test_clean_command_needs_no_model_call(self):
        memory = {"batches": [{"at": "10-01", "t": 1, "directions": ["A"]}]}
        p = ScriptedProvider([])
        result = agent.Agent(p).handle(None, "清理记忆", memory=memory)
        self.assertEqual(p.calls + p.classified, 0)
        self.assertEqual(result["status"], "complete")
        self.assertIn("清理好了", result["text"])
        self.assertEqual(result["trace"]["intent"], "clean_memory")


class CompressHistoryTests(unittest.TestCase):
    def test_twelve_turns_compress_to_summary_plus_recent_six(self):
        a = agent.Agent(agent.MockProvider())
        sid = None
        for i in range(12):
            sid = a.handle(sid, f"第{i}轮：群面一般怎么准备")["session_id"]
        session = a.sessions[sid]
        self.assertEqual(len(session.history), 6)
        self.assertEqual(session.summary, "（模拟模型）早期对话要点")
        a.handle(sid, "那笔试呢")
        self.assertEqual(len(session.history), 7)

    def test_summary_falls_back_when_model_fails(self):
        p = ScriptedProvider([out(None)] * 12, intent="general_advice", role=None)  # 压缩调用拿不到 json summary
        a = agent.Agent(p)
        sid = None
        for i in range(12):
            sid = a.handle(sid, f"问题{i}")["session_id"]
        session = a.sessions[sid]
        self.assertEqual(len(session.history), 6)
        self.assertIn("问题0", session.summary)


if __name__ == "__main__":
    unittest.main()
