"""城市产业资料（docs/research/city-industry-2026-10.md）：按提到的城市附上带出处的产业摘要；城市 + 岗位多/好找/门槛不严 打回重写。"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT / "tests"))
import agent  # noqa: E402
from test_profile import CARD, CANDS, chat_out  # noqa: E402
from test_web_agent import ScriptedProvider  # noqa: E402


class CityFactsTests(unittest.TestCase):
    def test_known_city_gets_sourced_summary(self):
        text = agent.city_facts(["我想去杭州"])
        self.assertIn("杭州：三次产业结构 1.7:25.3:73.0（据杭州2024年统计公报）", text)
        self.assertIn("数字经济", text)

    def test_unknown_city_gets_nothing(self):
        self.assertEqual(agent.city_facts(["我想回老家岳阳"]), "")

    def test_at_most_two_cities(self):
        self.assertEqual(agent.city_facts(["北京上海广州深圳都行"]).count("\n") + 1, 2)


class CityClaimTests(unittest.TestCase):
    def test_round18_sentence_is_caught(self):
        self.assertTrue(agent.city_claim("杭州这边中型公司和小公司里，这类岗位招应届生时对学校卡得没那么死。"))
        self.assertTrue(agent.city_claim("杭州电商岗位多，好找工作"))
        self.assertTrue(agent.city_claim("当地这类机会比较多"))

    def test_industry_scale_with_source_is_allowed(self):
        self.assertIsNone(agent.city_claim("据杭州2024年统计公报，数字经济核心产业占GDP的28.8%，是政府重点发展方向。"))
        self.assertIsNone(agent.city_claim("你想留在杭州，这个我记下了"))
        self.assertIsNone(agent.city_claim("这类岗位要求文字功底"))  # 没提城市，不算城市判断


class CityFlowTests(unittest.TestCase):
    def test_card_city_puts_facts_in_prompt_and_claim_is_rewritten(self):
        bad = json.loads(chat_out("你想先了解哪一个？", candidates=CANDS))
        bad["answer"] = "杭州这边内容岗位多，好找。"
        good = chat_out("你想先了解哪一个？", candidates=CANDS)
        p = ScriptedProvider([json.dumps(bad, ensure_ascii=False), good], intent="direction", role=None)
        result = agent.Agent(p).handle(None, agent.CARD_DONE, card=CARD)
        self.assertIn("<city_facts>", p.prompts[0])
        self.assertIn("据杭州2024年统计公报", p.prompts[0])
        self.assertIn("不能对城市的岗位多少", result["trace"]["attempts"][0][0])
        self.assertEqual(result["status"], "complete")


if __name__ == "__main__":
    unittest.main()
