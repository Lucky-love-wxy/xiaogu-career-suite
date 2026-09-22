import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "xiaogu-career-master" / "scripts" / "route_request.py"
SPEC = importlib.util.spec_from_file_location("route_request", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class HarnessRoutingTests(unittest.TestCase):
    def test_simple_job_understanding_routes_to_core_suite(self):
        result = MODULE.route("算法工程师每天到底是做什么的？")
        self.assertEqual(result["pipeline"], ["xiaogu-career-suite"])

    def test_resume_request_chains_job_understanding_first(self):
        result = MODULE.route("根据这份产品经理 JD 和我的项目经历改简历")
        self.assertEqual(result["pipeline"], ["xiaogu-career-suite", "xiaogu-resume"])
        self.assertIn("经过本人确认的经历或现有简历", result["missing_inputs"])

    def test_saved_material_context_avoids_reasking(self):
        result = MODULE.route(
            "根据这份产品经理 JD 和我的项目经历改简历",
            {"has_job_description": True, "has_candidate_experience": True},
        )
        self.assertEqual(result["missing_inputs"], [])

    def test_interview_review_requires_transcript_when_missing(self):
        result = MODULE.route("帮我复盘产品经理面试")
        self.assertEqual(result["pipeline"], ["xiaogu-career-suite", "xiaogu-interview-review"])
        self.assertIn("逐字稿或完整面试问答", result["missing_inputs"])

    def test_maimai_research_uses_optional_web_access_then_core(self):
        result = MODULE.route("去脉脉看看真实员工怎么说，算法工程师到底是做什么的")
        self.assertEqual(result["pipeline"], ["web-access", "xiaogu-career-suite"])

    def test_unknown_request_asks_one_choice_question(self):
        result = MODULE.route("帮我处理一下")
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIn("找岗位", result["question"])

    def test_master_workspace_is_standalone(self):
        script = ROOT / "skills" / "xiaogu-career-master" / "scripts" / "career_workspace.py"
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                [sys.executable, str(script), "--workspace", directory, "init"],
                check=True,
                capture_output=True,
                text=True,
            )
            status = subprocess.run(
                [sys.executable, str(script), "--workspace", directory, "status"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(json.loads(status.stdout)["ok"])


if __name__ == "__main__":
    unittest.main()
