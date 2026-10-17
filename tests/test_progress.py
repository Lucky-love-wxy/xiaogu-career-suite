"""求职进度看板（测试版，beta.progress）：漏斗逐段点亮、计划进度、7 天没动静、接口、对话联动。"""

import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT / "platform"))
sys.path.insert(0, str(ROOT / "tests"))
import progress  # noqa: E402
from store import Store  # noqa: E402

try:
    from test_platform import PlatformCase
except unittest.SkipTest:
    PlatformCase = None


def app(stage, outcome=None, days_ago=0, id_="x"):
    return {"id": id_, "stage": stage, "outcome": outcome, "stage_at": time.time() - days_ago * 86400}


class SummaryTests(unittest.TestCase):
    def test_funnel_lights_every_stage_reached(self):
        s = progress.summarize({"target_count": 100, "deadline": None, "target_offers": 1},
                               [app("interview"), app("applied"), app("want")])
        counts = {x["key"]: x["count"] for x in s["stages"]}
        self.assertEqual(counts, {"want": 3, "applied": 2, "test": 1, "interview": 1, "offer": 0})
        self.assertEqual([x["lit"] for x in s["stages"]], [True, True, True, True, False])
        self.assertEqual(s["plan_progress"], {"applied": 2, "target": 100, "percent": 2})

    def test_seven_days_without_movement_is_flagged(self):
        s = progress.summarize(None, [app("applied", days_ago=8, id_="old"), app("applied", days_ago=2, id_="new"),
                                      app("applied", outcome="rejected", days_ago=30, id_="done")])
        self.assertEqual(s["stale"], ["old"])
        self.assertEqual(s["rejected"], 1)
        self.assertIsNone(s["plan_progress"]["percent"])


class FeedbackLinkTests(unittest.TestCase):
    def test_company_required_and_stage_only_moves_forward(self):
        store = Store(":memory:")
        noted = progress.apply_feedback(store, "u", [{"kind": "投了", "company": "字节跳动", "role": "产品经理"},
                                                     {"kind": "投了", "detail": "又投了 10 份"}])  # 没说公司：不记
        self.assertEqual(noted, ["字节跳动"])
        progress.apply_feedback(store, "u", [{"kind": "有面试", "company": "字节跳动"}])
        progress.apply_feedback(store, "u", [{"kind": "投了", "company": "字节跳动"}])  # 不倒退
        apps = store.list_applications("u")
        self.assertEqual(len(apps), 1)
        self.assertEqual((apps[0]["stage"], apps[0]["role"], apps[0]["source"]), ("interview", "产品经理", "chat"))


@unittest.skipIf(PlatformCase is None, "缺少 web/requirements-dev.txt")
class ProgressApiTests(PlatformCase or unittest.TestCase):
    def test_hidden_until_beta_flag_is_on(self):
        client = self.login()
        self.assertEqual(client.get("/api/progress").status_code, 404)
        self.assertFalse(client.get("/api/meta").json()["beta"]["progress"])

    def test_plan_add_advance_outcome_delete(self):
        client = self.login()
        self.store.set_flag("beta.progress", "1", "test")
        self.assertTrue(client.get("/api/meta").json()["beta"]["progress"])
        view = client.post("/api/progress/plan", json={"target_count": 100, "deadline": "2026-12-31", "target_offers": 2}).json()
        self.assertEqual(view["summary"]["plan_progress"]["target"], 100)
        view = client.post("/api/applications", json={"company": "字节跳动", "role": "产品经理", "channel": "官网"}).json()
        app_id = view["applications"][0]["id"]
        self.assertEqual(view["summary"]["plan_progress"]["applied"], 1)
        view = client.post(f"/api/applications/{app_id}", json={"stage": "interview"}).json()
        self.assertTrue(view["summary"]["stages"][3]["lit"])
        view = client.post(f"/api/applications/{app_id}", json={"outcome": "rejected"}).json()
        self.assertEqual(view["summary"]["rejected"], 1)
        self.assertEqual(client.post("/api/applications", json={"company": ""}).status_code, 400)
        self.assertEqual(client.delete(f"/api/applications/{app_id}", headers={"content-type": "application/json"}).json()["applications"], [])

    def test_other_users_cannot_touch_my_applications(self):
        me = self.login()
        self.store.set_flag("beta.progress", "1", "test")
        app_id = me.post("/api/applications", json={"company": "字节跳动"}).json()["applications"][0]["id"]
        other = self.login(contact="13800002222")
        self.assertEqual(other.post(f"/api/applications/{app_id}", json={"stage": "offer"}).status_code, 404)
        self.assertEqual(other.get("/api/progress").json()["applications"], [])


if __name__ == "__main__":
    unittest.main()
