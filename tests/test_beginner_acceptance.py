"""Behavioral acceptance checks using ordinary beginner requests and clean installs."""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ROUTER = module("beginner_router", ROOT / "skills/xiaogu-career-master/scripts/route_request.py")
RENDERER = module("beginner_renderer", ROOT / "skills/xiaogu-career-master/scripts/render_response.py")


class BeginnerAcceptanceTests(unittest.TestCase):
    def test_first_use_is_guided_before_external_job_search(self):
        route = ROUTER.route("我没用过AI，想找工作，从哪开始？")
        self.assertEqual(route["pipeline"], ["xiaogu-career-master"])

    def test_concrete_question_is_not_lost_in_first_use(self):
        self.assertEqual(ROUTER.route("我第一次用AI，扁平化管理是啥？")["pipeline"], ["xiaogu-career-suite"])

    def test_ordinary_job_questions_request_actual_material(self):
        for query in ("这份工作靠谱吗？", "帮我看看这个招聘要求", "这个职位我能做吗？"):
            with self.subTest(query=query):
                result = ROUTER.route(query)
                self.assertEqual(result["pipeline"], ["xiaogu-career-suite"])
                self.assertEqual(result["missing_inputs"], ["岗位名称或 JD"])

    def test_interview_without_jd_asks_for_interview_record_first(self):
        for query in ("我刚面试完，不知道哪里答得不好", "我只有面试回忆，没有录音也能帮我吗？"):
            with self.subTest(query=query):
                result = ROUTER.route(query)
                self.assertEqual(result["primary_skill"], "xiaogu-interview-review")
                self.assertEqual(result["missing_inputs"], ["逐字稿或完整面试问答"])

    def test_short_explicit_material_and_mixed_intent(self):
        job = ROUTER.route("帮我看招聘说明：程序员，负责写代码，要求本科。")
        self.assertEqual(job["pipeline"], ["xiaogu-career-suite"])
        self.assertEqual(job["missing_inputs"], [])
        review = ROUTER.route("帮我复盘面试：面试官问为什么离职，我回答工资低。")
        self.assertEqual(review["primary_skill"], "xiaogu-interview-review")
        self.assertEqual(review["missing_inputs"], [])
        for query in ("我的投递没回复，公司说14薪是什么意思？", "我的投递没回复，帮我看看招聘说明：程序员，负责写代码，要求本科。"):
            self.assertEqual(ROUTER.route(query)["pipeline"], ["xiaogu-career-suite"])
        mixed = ROUTER.route("我刚面试完，想复盘一下，投递也一直没消息")
        self.assertEqual(mixed["primary_skill"], "xiaogu-interview-review")

    def test_no_response_does_not_assume_resume_is_the_cause(self):
        result = ROUTER.route("我投了好多简历都没回音")
        self.assertEqual(result["pipeline"], ["xiaogu-career-master"])

    def test_all_dictionary_phrases_are_discoverable_without_jd(self):
        rows = json.loads((ROOT / "database/jargon.json").read_text(encoding="utf-8"))
        for row in rows:
            with self.subTest(term=row["term"]):
                result = ROUTER.route(row["term"] + "是什么意思？")
                self.assertIn("xiaogu-career-suite", result["pipeline"])
                self.assertNotIn("岗位名称或 JD", result["missing_inputs"])

    def test_salary_spaces_do_not_prevent_routing(self):
        result = ROUTER.route("公司说14 薪，真的假的？")
        self.assertEqual(result["pipeline"], ["xiaogu-career-suite"])

    def test_salary_spaces_are_preserved_in_dictionary_match(self):
        search = module("beginner_search", ROOT / "skills/xiaogu-career-suite/scripts/search.py")
        result = search.search_jargon("公司说14 薪，是什么意思？")
        self.assertEqual(result["status"], "matched")
        self.assertEqual(result["matches"][0]["term"], "14薪")
        self.assertEqual(result["matches"][0]["matched_text"], "14 薪")

    def test_structural_internal_output_is_rejected(self):
        for text in ("primary_skill: xiaogu-resume", "请运行 render_response.py", "candidate_confirmed"):
            payload = {"status": "complete", "answer": text, "evidence": [], "unknown": [], "next_action": None}
            self.assertTrue(RENDERER.validate(payload))

    def test_multiple_questions_are_rejected(self):
        self.assertTrue(RENDERER.validate({"status": "needs_input", "question": "什么岗位？什么城市？"}))

    def test_agent_comparison_ignores_compound_command_notices(self):
        runner = module("beginner_runner", ROOT / "scripts/run_agent_acceptance.py")
        payload = {"status": "needs_input", "question": "你想应聘什么岗位？"}
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            (workspace / "response.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            command = '/bin/zsh -lc "python3 .agents/skills/xiaogu-career-master/scripts/render_response.py response.json"'
            event = {"type": "item.completed", "item": {"type": "command_execution", "command": command, "exit_code": 0, "aggregated_output": "Success. Updated files.\n你想应聘什么岗位？\n"}}
            trace = workspace / "trace.jsonl"
            trace.write_text(json.dumps(event), encoding="utf-8")
            self.assertTrue(runner.evaluate("你想应聘什么岗位？", workspace, trace)["final_equals_renderer"])
            self.assertFalse(runner.evaluate("任意改写", workspace, trace)["final_equals_renderer"])

    def test_optional_skills_validate_in_clean_install(self):
        artifacts = {
            "resume": {"bullets": [{"text": "负责课程项目中的数据清洗", "evidence_ids": ["test-user-message-1"], "verification_status": "confirmed"}]},
            "review": {"question_reviews": [{"source_quote": {"text": "我先去看日志"}, "diagnosis": "尚未说明如何定位问题", "fact_status": "transcript_fact"}]},
        }
        with tempfile.TemporaryDirectory() as directory:
            install = Path(directory)
            for kind, payload in artifacts.items():
                skill = "xiaogu-resume" if kind == "resume" else "xiaogu-interview-review"
                target = install / skill
                shutil.copytree(ROOT / "skills" / skill, target)
                data = install / (kind + ".json")
                data.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                result = subprocess.run([sys.executable, str(target / "scripts" / ("validate_" + kind + ".py")), str(data)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
