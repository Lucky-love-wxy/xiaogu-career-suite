import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "database" / "jargon.json"
VALIDATOR = ROOT / "scripts" / "validate_jargon.py"
SPEC = importlib.util.spec_from_file_location("validate_jargon", VALIDATOR)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class JargonQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(DATABASE.read_text(encoding="utf-8"))
        cls.by_term = {row["term"]: row for row in cls.rows}

    def test_schema_and_uniqueness(self):
        self.assertEqual(MODULE.validate(self.rows), [])
        self.assertEqual(len(self.rows), 46)

    def test_high_risk_recruiting_phrases_are_covered(self):
        for term in (
            "结果导向",
            "能承受高强度工作",
            "不强制加班",
            "有竞争力的薪酬",
            "晋升通道透明",
            "试用期6个月",
            "五险一金按Base缴纳",
            "期权激励",
            "末位淘汰",
        ):
            self.assertIn(term, self.by_term)

    def test_blunt_content_remains_conditional_and_actionable(self):
        for row in self.rows:
            self.assertTrue(row["blunt"])
            self.assertTrue(row["worst_case"])
            self.assertIn("不是对具体公司的事实判断", row["evidence_boundary"])
            self.assertGreaterEqual(len(row["red_flags"]), 2)
            self.assertIn("？", row["verify"])


if __name__ == "__main__":
    unittest.main()
