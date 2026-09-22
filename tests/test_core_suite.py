import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "xiaogu-career-suite" / "scripts"


class CoreSuiteTests(unittest.TestCase):
    def analyze(self, query: str) -> dict:
        process = subprocess.run(
            [sys.executable, str(SCRIPTS / "analyze_job.py"), "--query", query],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(process.stdout)

    def test_negation_and_internal_conflict_are_preserved(self):
        result = self.analyze("算法工程师，月薪20K，双休，但项目执行大小周，不涉及模型部署")
        conflicts = [item["text"] for item in result["card"]["conflicts"]]
        self.assertTrue(any("双休" in item for item in conflicts))
        self.assertTrue(any("模型部署" in item for item in conflicts))
        self.assertTrue(all(item["status"] == "reference" for item in result["card"]["daily_work"]))

    def test_index_miss_does_not_invent_occupation(self):
        result = self.analyze("宠物营养师，月薪面议")
        self.assertEqual(result["match"]["status"], "index_miss")
        self.assertIsNone(result["card"]["plain_language"])

    def test_card_validator_accepts_untampered_and_rejects_tampered(self):
        result = self.analyze("算法工程师，月薪20K，双休")
        with tempfile.TemporaryDirectory() as directory:
            card = Path(directory) / "card.json"
            card.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            valid = subprocess.run([sys.executable, str(SCRIPTS / "validate_card.py"), str(card)])
            self.assertEqual(valid.returncode, 0)
            result["card"]["jd_facts"][0]["text"] = "月薪50K"
            card.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
            invalid = subprocess.run([sys.executable, str(SCRIPTS / "validate_card.py"), str(card)])
            self.assertNotEqual(invalid.returncode, 0)


if __name__ == "__main__":
    unittest.main()
