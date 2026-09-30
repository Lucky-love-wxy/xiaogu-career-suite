import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "xiaogu-career-master" / "scripts" / "route_request.py"
RENDERER = ROOT / "skills" / "xiaogu-career-master" / "scripts" / "render_response.py"
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

    def test_standalone_jargon_does_not_require_job_description(self):
        for phrase in ("扁平化管理是什么意思？", "14薪和团建怎么算？"):
            result = MODULE.route(phrase)
            self.assertEqual(result["pipeline"], ["xiaogu-career-suite"])
            self.assertEqual(result["missing_inputs"], [])

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


class HarnessOutputTests(unittest.TestCase):
    def render(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "response.json"
            source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(RENDERER), str(source)],
                capture_output=True, text=True,
            )

    def test_evidence_order_and_single_next_action(self):
        result = self.render({
            "status": "complete",
            "answer": "扁平化管理通常指层级少。",
            "evidence": [{"kind": "reference", "text": "词典中的一般解释"}],
            "unknown": ["目标团队的实际汇报关系"],
            "next_action": "问清谁分派任务和谁评绩效。",
        })
        self.assertEqual(result.returncode, 0)
        self.assertLess(result.stdout.index("**结论**"), result.stdout.index("**依据**"))
        self.assertLess(result.stdout.index("**依据**"), result.stdout.index("**仍需确认**"))
        self.assertLess(result.stdout.index("**仍需确认**"), result.stdout.index("**下一步**"))
        self.assertNotIn("xiaogu-career-suite", result.stdout)

    def test_missing_input_asks_only_one_question(self):
        result = self.render({"status": "needs_input", "question": "请提供逐字稿或完整问答？"})
        self.assertEqual(result.stdout, "请提供逐字稿或完整问答？\n")

    def test_invalid_evidence_label_is_rejected(self):
        result = self.render({
            "status": "complete", "answer": "已通过面试。",
            "evidence": [{"kind": "company_fact", "text": "匿名评论"}],
            "unknown": [], "next_action": None,
        })
        self.assertNotEqual(result.returncode, 0)

    def test_blocker_is_visible_and_preserves_partial_result(self):
        result = self.render({
            "status": "blocked", "answer": "已整理岗位要求。",
            "evidence": [], "unknown": ["从业者实际反馈"],
            "blocker": "公开页面要求登录。", "next_action": "请提供帖子链接或截图。",
        })
        self.assertEqual(result.returncode, 0)
        self.assertIn("已整理岗位要求", result.stdout)
        self.assertIn("**受阻原因** 公开页面要求登录。", result.stdout)


if __name__ == "__main__":
    unittest.main()
