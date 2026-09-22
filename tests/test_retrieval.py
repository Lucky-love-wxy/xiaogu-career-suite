import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/xiaogu_search.py"


def run(kind, query):
    process = subprocess.run(
        [sys.executable, str(SCRIPT), kind, "--query", query],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(process.stdout)


class RetrievalTests(unittest.TestCase):
    def test_retrieval(self):
        result = run("jargon", "结果导向与弹性工作")
        self.assertEqual(result["status"], "matched")
        self.assertEqual(len(result["matches"]), 2)

        result = run("occupation", "推荐算法工程师负责模型和线上实验")
        self.assertEqual(result["matches"][0]["id"], "recommendation-algorithm-engineer")

        result = run("occupation", "宠物营养师")
        self.assertEqual(result["status"], "index_miss")

        result = run("analyze", "数据工程师，快速迭代")
        self.assertEqual(result["jargon"]["status"], "matched")
        self.assertEqual(result["occupation"]["status"], "matched")


if __name__ == "__main__":
    unittest.main()
