import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTER = ROOT / "skills" / "xiaogu-career-master" / "scripts" / "route_request.py"
RENDERER = ROOT / "skills" / "xiaogu-career-master" / "scripts" / "render_response.py"
MOCK = ROOT / "examples" / "algorithm-engineer-mock"
SPEC = importlib.util.spec_from_file_location("route_request_live", ROUTER)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def render(payload):
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "response.json"
        source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return subprocess.run([sys.executable, str(RENDERER), str(source)], capture_output=True, text=True)


class LiveSourceRoutingTests(unittest.TestCase):
    def test_job_understanding_defaults_to_live_sources_without_naming_them(self):
        result = MODULE.route("算法工程师每天到底是做什么的？")
        self.assertEqual(result["live_sources"], ["nowcoder", "maimai"])
        self.assertEqual(result["pipeline"], ["xiaogu-career-suite"])

    def test_jargon_resume_and_interview_do_not_go_online_by_default(self):
        for query in (
            "扁平化管理是什么意思？", "结果导向是什么意思？", "快速迭代什么意思", "薪资面议怎么理解",
            "根据这份产品经理 JD 和我的项目经历改简历", "帮我复盘产品经理面试",
        ):
            self.assertEqual(MODULE.route(query)["live_sources"], [], query)

    def test_role_with_jargon_still_goes_online(self):
        self.assertEqual(MODULE.route("推荐算法工程师，结果导向，快速迭代")["live_sources"], ["nowcoder", "maimai"])


class ExternalEvidenceTests(unittest.TestCase):
    BASE = {"status": "complete", "answer": "结论。", "unknown": [], "next_action": None}

    def test_external_report_requires_link_date_and_source(self):
        result = render({**self.BASE, "evidence": [{"kind": "external_report", "text": "有人说大小周"}]})
        self.assertNotEqual(result.returncode, 0)

    def test_mock_link_rejected_outside_fixture(self):
        item = {"kind": "external_report", "text": "有人说大小周", "url": "mock://nowcoder/p1", "date": "2026-07", "source_name": "牛客"}
        self.assertNotEqual(render({**self.BASE, "evidence": [item]}).returncode, 0)
        self.assertEqual(render({**self.BASE, "fixture": True, "evidence": [item]}).returncode, 0)

    def test_external_report_label_and_citation_visible(self):
        item = {"kind": "external_report", "text": "有人说大小周", "url": "https://example.com/p", "date": "2026-07", "source_name": "牛客"}
        result = render({**self.BASE, "evidence": [item]})
        self.assertIn("从业者分享（未核实）：有人说大小周（牛客，2026-07，https://example.com/p）", result.stdout)


class MockFixtureTests(unittest.TestCase):
    def test_every_fixture_renders_exactly_to_expected(self):
        responses = sorted((MOCK / "responses").glob("*.json"))
        self.assertGreaterEqual(len(responses), 10)
        for source in responses:
            result = subprocess.run([sys.executable, str(RENDERER), str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, source.name)
            self.assertEqual(result.stdout, (MOCK / "expected" / f"{source.stem}.md").read_text(encoding="utf-8"), source.name)

    def test_mock_posts_cannot_pass_as_real(self):
        data = json.loads((MOCK / "live_sources.json").read_text(encoding="utf-8"))
        self.assertIn("模拟数据", data["notice"])
        for post in data["posts"]:
            self.assertTrue(post["mock"])
            self.assertTrue(post["url"].startswith("mock://"))
            self.assertLessEqual(len(post["claims"][0]["quote"]), 30)
        self.assertIn("模拟数据", (MOCK / "jd.txt").read_text(encoding="utf-8"))


class RealFixtureTests(unittest.TestCase):
    def test_real_fixture_preserves_schema_and_uncertainty(self):
        real = json.loads((ROOT / "examples/algorithm-engineer-real/live_sources.json").read_text())
        mock = json.loads((MOCK / "live_sources.json").read_text())
        self.assertEqual(set(real), set(mock))
        self.assertEqual(real["scope_values"], mock["scope_values"])
        self.assertEqual(len(real["posts"]), 3)
        ids = {p["id"] for p in real["posts"]}
        for post in real["posts"]:
            self.assertEqual(set(post), set(mock["posts"][0]))
            self.assertFalse(post["mock"])
            self.assertTrue(post["url"].startswith("https://www.nowcoder.com/"))
            self.assertNotEqual(post["scope"], "same_company")
            for claim in post["claims"]:
                self.assertEqual(set(claim), {"topic", "paraphrase", "quote"})
                self.assertLessEqual(len(claim["quote"]), 30)
        self.assertIn("年份", real["posts"][2]["posted_at"])
        for scenario in real["scenarios"].values():
            self.assertEqual(scenario["sources"]["maimai"]["status"], "skipped_robots")
            self.assertTrue(set(scenario["sources"]["nowcoder"]["posts"]) <= ids)

    def test_real_citation_renders_without_mock_permission(self):
        real = json.loads((ROOT / "examples/algorithm-engineer-real/live_sources.json").read_text())
        post = real["posts"][0]
        result = render({"status": "complete", "answer": "仅讨论这条历史分享。", "unknown": [],
                         "next_action": None, "evidence": [{"kind": "external_report",
                         "text": post["claims"][0]["paraphrase"], "url": post["url"],
                         "date": post["posted_at"][:10], "source_name": post["source_name"]}]})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(post["url"], result.stdout)
        self.assertIn("从业者分享（未核实）", result.stdout)


if __name__ == "__main__":
    unittest.main()
