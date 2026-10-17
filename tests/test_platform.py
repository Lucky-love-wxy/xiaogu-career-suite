"""上线平台层（web/app.py、store.py、auth.py）：登录、额度、计量、隔离、开关、熔断、并发、后台。
全部用假模型，不花钱。需要 web/requirements-dev.txt（httpx）。"""

import json
import math
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
sys.path.insert(0, str(ROOT / "platform"))
import agent  # noqa: E402

try:
    from fastapi.testclient import TestClient
    import app as webapp
    from store import Store
except ImportError as exc:  # 没装 web/requirements-dev.txt 时跳过，不影响原有测试
    raise unittest.SkipTest(f"缺少依赖：{exc}")

JD = (ROOT / "examples" / "algorithm-engineer-mock" / "jd.txt").read_text(encoding="utf-8")
CALL_USAGE = {"prompt_tokens": 10_000, "prompt_cache_hit_tokens": 2_000, "completion_tokens": 1_000}
# v4-pro 单价 3 / 0.025 / 6 元每百万：8000*3 + 2000*0.025 + 1000*6 = 30050 / 1e6 = ¥0.03005 每次调用
CALL_COST = 0.03005


class MeteredMock(agent.MockProvider):
    """模拟模型 + 假装每次调用都按 v4-pro 计费，用来测计量和扣费。delay 用来测并发。"""
    name, model = "deepseek", "deepseek-v4-pro"

    def __init__(self, delay: float = 0.0, broken: bool = False):
        super().__init__()
        self.delay, self.broken = delay, broken

    def complete(self, messages):
        if self.delay:
            time.sleep(self.delay)
        bucket = agent.USAGE.get()
        if bucket is not None:
            bucket.append({"model": self.model, "usage": dict(CALL_USAGE)})
        if self.broken and "意图分类器" not in messages[0]["content"]:
            return "{}"  # 每次都过不了校验：最终“受阻”
        return super().complete(messages)


class PlatformCase(unittest.TestCase):
    provider_kwargs: dict = {}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        cfg = webapp.Config({"XIAOGU_ENV": "dev", "XIAOGU_ADMIN_TOKEN": "admin-pass",
                             "XIAOGU_DB": str(Path(self.tmp.name) / "t.db")})
        self.platform = webapp.Platform(cfg, provider=MeteredMock(**self.provider_kwargs))
        self.store = self.platform.store
        self.app = webapp.create_app(self.platform)
        self.invite = self.store.create_invites(10, 500, max_uses=10)[0]

    def tearDown(self):
        self.tmp.cleanup()

    def login(self, contact="13800001111", invite=None, consent=True) -> TestClient:
        client = TestClient(self.app)
        sent = client.post("/api/auth/code", json={"contact": contact})
        self.assertEqual(sent.status_code, 200, sent.text)
        res = client.post("/api/auth/verify", json={"contact": contact, "code": sent.json()["dev_code"],
                                                     "invite": invite if invite is not None else self.invite,
                                                     "consent": consent})
        self.assertEqual(res.status_code, 200, res.text)
        return client

    def chat(self, client, message, session_id=None):
        return client.post("/api/chat", json={"message": message, "session_id": session_id})


class AuthTests(PlatformCase):
    def test_new_user_needs_invite_and_consent_and_gets_500_credits(self):
        client = TestClient(self.app)
        code = client.post("/api/auth/code", json={"contact": "13800002222"}).json()["dev_code"]
        no_invite = client.post("/api/auth/verify", json={"contact": "13800002222", "code": code, "consent": True})
        self.assertEqual(no_invite.status_code, 400)
        self.assertIn("邀请码", no_invite.json()["error"])
        no_consent = client.post("/api/auth/verify", json={"contact": "13800002222", "code": code, "invite": self.invite})
        self.assertIn("同意", no_consent.json()["error"])
        ok = client.post("/api/auth/verify", json={"contact": "13800002222", "code": code, "invite": self.invite,
                                                    "consent": True})
        self.assertEqual(ok.status_code, 200, ok.text)
        me = client.get("/api/me").json()
        self.assertEqual(me["balance"], 500)
        self.assertEqual(me["contact"], "138****2222")

    def test_email_hyphen_and_plus_survive_registration(self):
        client = self.login(contact="Test-User+job@EXAMPLE.COM")
        self.assertEqual(client.get("/api/me").status_code, 200)
        self.assertIsNotNone(self.store.user_by_contact("test-user+job@example.com"))
        self.assertIsNone(self.store.user_by_contact("testuser+job@example.com"))

    def test_wrong_code_is_rejected_and_limited(self):
        client = TestClient(self.app)
        client.post("/api/auth/code", json={"contact": "a@b.com"})
        for _ in range(5):
            self.assertEqual(client.post("/api/auth/verify", json={"contact": "a@b.com", "code": "000000x",
                                                                    "invite": self.invite, "consent": True}).status_code, 400)
        res = client.post("/api/auth/verify", json={"contact": "a@b.com", "code": "x", "invite": self.invite, "consent": True})
        self.assertIn("次数过多", res.json()["error"])

    def test_api_requires_login_and_json(self):
        client = TestClient(self.app)
        self.assertEqual(client.post("/api/chat", json={"message": "hi"}).status_code, 401)
        self.assertEqual(client.post("/api/chat", content="message=hi",
                                     headers={"content-type": "application/x-www-form-urlencoded"}).status_code, 415)

    def test_prod_refuses_console_sender_and_missing_secrets(self):
        with self.assertRaises(SystemExit):
            webapp.Config({"XIAOGU_ENV": "prod", "XIAOGU_SECRET": "s", "XIAOGU_ADMIN_TOKEN": "a"})
        with self.assertRaises(SystemExit):
            webapp.Config({"XIAOGU_ENV": "prod", "XIAOGU_LOGIN_SENDER": "sms"})

    def test_prod_never_falls_back_to_mock_or_simulated_sources(self):
        ready = {"XIAOGU_ENV": "prod", "XIAOGU_SECRET": "s", "XIAOGU_ADMIN_TOKEN": "a", "XIAOGU_LOGIN_SENDER": "sms"}
        with self.assertRaises(SystemExit) as mock:
            webapp.Config({**ready, "XIAOGU_PROVIDER": "mock"})
        self.assertIn("mock", str(mock.exception))
        # 10-14 起网页版不再查从业者帖子（原来读的是模拟帖子，RUNBOOK B5），这道检查不再挡；
        # 但检查本身留着：以后谁把模拟来源接回 Agent，生产仍会拒绝启动
        import inspect
        self.assertNotIn("simulated_live_sources(", inspect.getsource(agent.Agent))
        with self.assertRaises(SystemExit) as gate:
            webapp.Config(ready)
        self.assertNotIn("B5", str(gate.exception))

    def test_staging_defaults_to_mock_model(self):
        self.assertEqual(webapp.Config({"XIAOGU_ENV": "staging"}).provider, "mock")


class BillingTests(PlatformCase):
    def test_turn_is_metered_per_call_and_charged(self):
        client = self.login()
        res = self.chat(client, "帮我看看这个岗位：\n" + JD)
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        calls = self.store.rows("SELECT * FROM llm_calls")
        self.assertGreaterEqual(len(calls), 1)
        self.assertAlmostEqual(calls[0]["cost_cny"], CALL_COST, places=6)
        self.assertEqual(calls[0]["cache_hit_tokens"], 2000)
        # 1 credit = ¥0.02（100 credits 对应后台 ¥2），按实际消耗向上取到 0.01 credit
        units = math.ceil(round(len(calls) * CALL_COST * 50 * 100, 6))
        expected = units / 100
        self.assertAlmostEqual(body["credits"]["charged"], expected, places=6)
        self.assertAlmostEqual(body["credits"]["balance"], 500 - expected, places=6)
        turn = self.store.one("SELECT * FROM turns")
        self.assertEqual(turn["feature"], "chat")
        self.assertEqual(turn["credits_charged"], units)  # 库里按 0.01 credit 记整数
        # 预扣已经全部退回：台账里 reserve 与 release 相抵
        r = self.store.one("SELECT SUM(credits) AS s FROM credit_ledger WHERE type IN ('reserve','release')")
        self.assertEqual(r["s"], 0)

    def test_exhausted_credits_return_402(self):
        client = self.login()
        user = self.store.user_by_contact("13800001111")
        self.store.adjust_credits(user["id"], -499.5, "测试")  # 剩 0.5，低于开始一轮的最低 1 credit
        res = self.chat(client, "你好")
        self.assertEqual(res.status_code, 402)
        self.assertEqual(self.store.one("SELECT COUNT(*) AS n FROM llm_calls")["n"], 0)

    def test_markup_flag_changes_charge(self):
        client = self.login()
        self.store.set_flag("markup", "2.0", "test")
        body = self.chat(client, "帮我看看这个岗位：\n" + JD).json()
        n = self.store.one("SELECT COUNT(*) AS n FROM llm_calls")["n"]
        self.assertAlmostEqual(body["credits"]["charged"], math.ceil(round(n * CALL_COST * 50 * 2 * 100, 6)) / 100, places=6)


class BlockedTurnTests(PlatformCase):
    provider_kwargs = {"broken": True}

    def test_blocked_turn_costs_us_but_not_the_user(self):
        client = self.login()
        body = self.chat(client, "帮我看看这个岗位：\n" + JD).json()
        self.assertEqual(body["status"], "blocked")
        self.assertEqual(body["credits"]["charged"], 0)
        self.assertEqual(body["credits"]["balance"], 500)
        self.assertGreater(self.store.one("SELECT SUM(cost_cny) AS s FROM llm_calls")["s"], 0)


class IsolationTests(PlatformCase):
    def test_other_users_session_is_invisible(self):
        a, b = self.login("13800001111"), self.login("13800003333")
        sid = self.chat(a, "帮我看看这个岗位：\n" + JD).json()["session_id"]
        self.assertEqual(self.chat(b, "继续", session_id=sid).status_code, 404)
        self.assertEqual(b.get(f"/api/sessions/{sid}").status_code, 404)
        self.assertEqual(a.get(f"/api/sessions/{sid}").status_code, 200)

    def test_session_survives_restart(self):
        a = self.login()
        sid = self.chat(a, "帮我看看这个岗位：\n" + JD).json()["session_id"]
        self.platform.agent.sessions.clear()
        self.platform.owners.clear()
        res = self.chat(a, "这个岗位要加班吗", session_id=sid)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["session_id"], sid)
        self.assertIsNotNone(self.platform.agent.sessions[sid].jd)  # 恢复后仍记得 JD

    def test_deleted_session_is_gone_for_user(self):
        a = self.login()
        sid = self.chat(a, "你好").json()["session_id"]
        self.assertEqual(a.delete(f"/api/sessions/{sid}", headers={"content-type": "application/json"}).status_code, 200)
        self.assertEqual(a.get("/api/sessions").json()["sessions"], [])
        self.assertEqual(self.chat(a, "继续", session_id=sid).status_code, 404)

    def test_delete_clears_content_but_keeps_billing_record(self):
        # 2026-10-14：删除即清除对话内容，只留不含内容的运行记录（计费核对、安全排查），6 个月后连记录一起删
        a = self.login()
        sid = self.chat(a, "我的秘密经历：在某公司实习").json()["session_id"]
        a.delete(f"/api/sessions/{sid}", headers={"content-type": "application/json"})
        with self.store.conn() as c:
            session = c.execute("SELECT state, title, deleted_at FROM chat_sessions WHERE id=?", (sid,)).fetchone()
            turns = c.execute("SELECT user_message, final_text, cost_cny, feature FROM turns WHERE session_id=?", (sid,)).fetchall()
        self.assertEqual((session["state"], session["title"]), ("{}", ""))
        self.assertIsNotNone(session["deleted_at"])
        self.assertTrue(turns)
        self.assertTrue(all(t["user_message"] is None and t["final_text"] is None for t in turns))
        self.assertTrue(all(t["feature"] for t in turns))


class SwitchTests(PlatformCase):
    def test_global_maintenance(self):
        client = self.login()
        self.store.set_flag("maintenance", "1", "test")
        res = self.chat(client, "你好")
        self.assertEqual(res.status_code, 503)

    def test_feature_switch_only_blocks_that_feature(self):
        client = self.login()
        self.store.set_flag("feature.interview", "0", "test")
        self.assertEqual(self.chat(client, "模拟面试：推荐算法工程师").status_code, 503)
        self.assertEqual(self.chat(client, "你好").status_code, 200)

    def test_suspended_user(self):
        client = self.login()
        user = self.store.user_by_contact("13800001111")
        self.store.set_user_status(user["id"], "suspended")
        self.assertEqual(self.chat(client, "你好").status_code, 403)

    def test_daily_cost_cap_trips_breaker(self):
        client = self.login()
        self.store.set_flag("daily_cost_cap_cny", "0.01", "test")
        self.assertEqual(self.chat(client, "帮我看看这个岗位：\n" + JD).status_code, 200)
        flags = self.store.flags()
        self.assertEqual(flags["maintenance"], "1")
        self.assertIn("自动暂停", flags["maintenance_reason"])
        self.assertEqual(self.chat(client, "你好").status_code, 503)

    def test_global_token_cap_blocks_all_users(self):
        client = self.login()
        with self.store.conn() as c:  # 模拟模型不产生 usage，直接写一条已消耗记录
            c.execute("INSERT INTO llm_calls(user_id, session_id, turn_id, model, prompt_tokens, cache_hit_tokens, "
                      "completion_tokens, cost_cny, created_at) VALUES ('u','s','t','mock',600,0,500,0,0)")
        self.store.set_flag("global_token_cap", "1000", "test")
        self.platform.breaker()
        self.assertEqual(self.store.flag("maintenance"), "1")
        # 后台解除暂停但没调高上限，仍然拦住；个人 credits 还有余额也一样
        self.store.set_flag("maintenance", "0", "admin")
        self.assertGreater(self.store.balance(self.store.user_by_contact("13800001111")["id"]), 0)
        self.assertEqual(self.chat(client, "你好").status_code, 503)
        self.store.set_flag("global_token_cap", "0", "admin")
        self.assertEqual(self.chat(client, "你好").status_code, 200)

    def test_low_provider_balance_trips_breaker(self):
        self.platform.provider_balance = {"total_cny": 5.0}
        self.platform.breaker()
        self.assertEqual(self.store.flag("maintenance"), "1")


class ConcurrencyTests(PlatformCase):
    provider_kwargs = {"delay": 0.4}

    def test_two_users_stream_in_parallel_without_crosstalk(self):
        a, b = self.login("13800001111"), self.login("13800003333")
        results: dict[str, list] = {}

        def run(name, client):
            events = []
            with client.stream("POST", "/api/chat/stream", json={"message": "帮我看看这个岗位：\n" + JD}) as res:
                for line in res.iter_lines():
                    if line.startswith("data: "):
                        events.append(json.loads(line[6:]))
            results[name] = events

        started = time.time()
        threads = [threading.Thread(target=run, args=("a", a)), threading.Thread(target=run, args=("b", b))]
        [t.start() for t in threads]
        [t.join(30) for t in threads]
        elapsed = time.time() - started
        calls = self.store.one("SELECT COUNT(*) AS n FROM llm_calls")["n"]
        # 串行需要 calls × 0.4 秒；并行应明显更快
        self.assertLess(elapsed, calls * 0.4 * 0.8, f"elapsed={elapsed:.2f}s calls={calls}")
        stages = {k: [e for e in v if e["type"] == "stage"] for k, v in results.items()}
        finals = {k: [e for e in v if e["type"] == "final"] for k, v in results.items()}
        self.assertEqual(len(finals["a"]), 1)
        self.assertEqual(len(finals["b"]), 1)
        self.assertNotEqual(finals["a"][0]["session_id"], finals["b"][0]["session_id"])
        self.assertEqual(len(stages["a"]), len(stages["b"]))  # 过程事件各收各的，不串到别人的流里
        self.assertGreater(len(stages["a"]), 0)


class AdminTests(PlatformCase):
    def test_dashboard_requires_admin_and_masks_contacts(self):
        user = self.login()
        self.chat(user, "帮我看看这个岗位：\n" + JD)
        admin = TestClient(self.app)
        self.assertEqual(admin.get("/api/admin/dashboard").status_code, 401)
        self.assertEqual(admin.post("/api/admin/login", json={"token": "wrong"}).status_code, 401)
        self.assertEqual(admin.post("/api/admin/login", json={"token": "admin-pass"}).status_code, 200)
        data = admin.get("/api/admin/dashboard").json()
        self.assertEqual(data["users"][0]["contact"], "138****1111")
        self.assertGreater(data["today"]["cost_cny"], 0)
        self.assertEqual(data["today"]["revenue_cny"], 0)
        self.assertLess(data["today"]["gross_profit_cny"], 0)  # 内测全是赠送：毛利为负，看板如实显示
        self.assertEqual(data["liability"]["credits_granted_total"], 500)
        uid = data["users"][0]["id"]
        turns = admin.get(f"/api/admin/users/{uid}/turns").json()["turns"]
        self.assertEqual(len(turns), 1)
        # 用户界面不能进后台
        self.assertEqual(user.get("/api/admin/dashboard").status_code, 401)

    def test_admin_actions(self):
        self.login()
        admin = TestClient(self.app)
        admin.post("/api/admin/login", json={"token": "admin-pass"})
        uid = self.store.user_by_contact("13800001111")["id"]
        self.assertEqual(admin.post(f"/api/admin/users/{uid}/credits", json={"credits": 100, "note": "补偿"}).json()["balance"], 600)
        admin.post(f"/api/admin/users/{uid}/status", json={"status": "suspended"})
        self.assertEqual(self.store.user(uid)["status"], "suspended")
        flags = admin.post("/api/admin/flags", json={"key": "maintenance", "value": "1"}).json()["flags"]
        self.assertEqual(flags["maintenance"], "1")
        self.assertEqual(admin.post("/api/admin/flags", json={"key": "nope", "value": "1"}).status_code, 400)
        codes = admin.post("/api/admin/invites", json={"count": 3, "credits": 500}).json()["codes"]
        self.assertEqual(len(codes), 3)


class NewApiUsageTests(PlatformCase):
    """new-api 系中转站：用 key 读用量，换算成美元显示，低于阈值熔断。用本机假服务器，不连外网。"""

    def start_router(self, usage_body):
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        seen = self.seen = []

        class Router(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                seen.append((self.path, self.headers.get("Authorization")))
                body = {"success": True, "data": {"quota_per_unit": 500000}} if self.path == "/api/status" else usage_body
                raw = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Router)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.addCleanup(server.shutdown)
        provider = self.platform.agent.provider
        provider.base_url, provider._key = f"http://127.0.0.1:{server.server_port}/v1", "sk-test"

    def test_usage_is_converted_and_shown(self):
        self.start_router({"code": True, "message": "ok", "data": {"object": "token_usage", "name": "xiaogu",
                           "total_granted": 10_000_000, "total_used": 2_500_000, "total_available": 7_500_000,
                           "unlimited_quota": False, "expires_at": 0}})
        self.platform.poll_provider_balance()
        bal = self.platform.provider_balance
        self.assertEqual((bal["kind"], bal["available_usd"], bal["used_usd"], bal["granted_usd"]), ("newapi", 15.0, 5.0, 20.0))
        self.assertIn(("/api/usage/token/", "Bearer sk-test"), self.seen)
        self.assertIn(("/api/status", None), self.seen)  # 公开接口不带 key
        self.assertEqual(self.store.flag("maintenance"), "0")

    def test_low_router_quota_trips_breaker(self):
        self.start_router({"data": {"total_used": 9_000_000, "total_available": 500_000, "unlimited_quota": False}})
        self.platform.poll_provider_balance()
        self.assertEqual(self.store.flag("maintenance"), "1")
        self.assertIn("中转站", self.store.flag("maintenance_reason"))

    def test_unlimited_key_never_trips(self):
        self.start_router({"data": {"total_used": 9_000_000, "total_available": 0, "unlimited_quota": True}})
        self.platform.poll_provider_balance()
        self.assertEqual(self.store.flag("maintenance"), "0")

    def test_cached_tokens_from_openai_style_usage(self):
        cost, tokens = self.store.call_cost("deepseek-v4-pro", {"prompt_tokens": 1000, "completion_tokens": 0,
                                                                 "prompt_tokens_details": {"cached_tokens": 1000}})
        self.assertEqual(tokens["cache_hit_tokens"], 1000)
        self.assertAlmostEqual(cost, 1000 * 0.025 / 1e6)

    def test_prod_refuses_third_party_router_without_explicit_ack(self):
        ready = {"XIAOGU_ENV": "prod", "XIAOGU_SECRET": "s", "XIAOGU_ADMIN_TOKEN": "a", "XIAOGU_LOGIN_SENDER": "sms",
                 "XIAOGU_BASE_URL": "https://router.example.com/v1"}
        with self.assertRaises(SystemExit) as refused:
            webapp.Config(ready)
        self.assertIn("B7", str(refused.exception))


class MaskTests(unittest.TestCase):
    def test_mask(self):
        from store import mask
        self.assertEqual(mask("电话 13912345678，邮箱 lucky@qq.com，身份证 110101199001011234"),
                         "电话 139****5678，邮箱 l***@qq.com，身份证 110101********1234")


if __name__ == "__main__":
    unittest.main()


class ProfileCardTests(PlatformCase):
    """基本情况卡片（notes/2026-10-14-基本情况卡片与对话标注修复.md）：按用户保存、可清空、每轮现读、不复制进会话状态。"""
    CARD = {"学校层级": "普通一本", "专业": "汉语言文学", "毕业时间": "2026届", "工作意愿": ["校招"], "意向城市": "杭州",
            "公司规模": ["都可以"], "期望月薪": "不确定", "实习经历": "在校报社写过 20 篇稿子"}

    def test_save_validate_clear(self):
        client = self.login()
        meta = client.get("/api/me/profile").json()
        self.assertEqual(meta["profile"], {})
        self.assertIn("城市偏好", meta["fields"])
        self.assertTrue(meta["fields"]["城市偏好"]["multi"])
        bad = client.post("/api/me/profile", json={"profile": {"学校": "某某大学"}})
        self.assertEqual(bad.status_code, 400)  # 必填项缺了不保存
        self.assertEqual(client.post("/api/me/profile", json={"profile": self.CARD}).status_code, 200)
        self.assertEqual(client.get("/api/me/profile").json()["profile"]["专业"], "汉语言文学")
        client.post("/api/me/profile", json={"profile": {}})
        self.assertEqual(client.get("/api/me/profile").json()["profile"], {})

    def test_other_user_cannot_see_card(self):
        self.login().post("/api/me/profile", json={"profile": self.CARD})
        other = self.login(contact="13800002222")
        self.assertEqual(other.get("/api/me/profile").json()["profile"], {})

    def test_card_drives_direction_and_never_lands_in_session_state(self):
        client = self.login()
        first = self.chat(client, "我不知道该投什么岗位").json()
        self.assertEqual(first["status"], "needs_input")
        self.assertEqual(first["action"], "profile_card")
        client.post("/api/me/profile", json={"profile": self.CARD})
        meta = client.get("/api/me/profile").json()
        done = self.chat(client, meta["done_message"], first["session_id"]).json()
        self.assertEqual(done["trace"]["route"]["task"], "propose")
        client.post("/api/me/profile", json={"profile": {}})  # 清空后，数据库里的会话不能还留着卡片内容
        with self.store.conn() as c:
            states = [r["state"] for r in c.execute("SELECT state FROM chat_sessions")]
        self.assertTrue(states)
        self.assertFalse(any("在校报社写过 20 篇稿子" in s for s in states))


class CreditUnitTests(unittest.TestCase):
    """10-14：100 credits = 后台 ¥2，按实际消耗扣到 0.01 credit；账本按 0.01 credit 记整数。"""

    def test_small_cost_is_charged_precisely_not_rounded_to_whole_credit(self):
        store = Store(":memory:")
        self.assertAlmostEqual(store.charge_for(0.0059), 0.3, places=6)   # 开发库实测单轮平均成本
        self.assertAlmostEqual(store.charge_for(0.00001), 0.01, places=6)  # 最少 0.01
        self.assertEqual(store.charge_for(0), 0)

    def test_old_ledger_is_migrated_once(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "old.db")
            Store(path)
            with sqlite3.connect(path) as c:  # 模拟迁移前的旧库：整数 credit，user_version=0
                c.execute("INSERT INTO credit_ledger(user_id, type, credits, created_at) VALUES ('u', 'grant', 500, 0)")
                c.execute("PRAGMA user_version = 0")
            self.assertAlmostEqual(Store(path).balance("u"), 500.0)
            self.assertAlmostEqual(Store(path).balance("u"), 500.0)  # 再开一次不会再乘 100


class MessageLimitTests(PlatformCase):
    def test_message_over_2000_chars_is_rejected_with_count(self):
        client = self.login()
        res = self.chat(client, "字" * 2001)
        self.assertEqual(res.status_code, 413)
        self.assertIn("2001", res.json()["error"])
        self.assertEqual(self.chat(client, "字" * 2000).status_code, 200)
        self.assertEqual(client.get("/api/meta").json()["max_message"], 2000)


class MemoryDocTests(PlatformCase):
    """用户记忆文档：按用户存、跨对话读、不进会话状态；对话满 10 个提醒一次清理。"""

    def test_memory_persists_across_conversations_and_stays_out_of_session_state(self):
        client = self.login()
        user = self.store.user_by_contact("13800001111")
        self.store.set_memory(user["id"], {"facts": {"意向城市": {"value": "杭州", "at": "10-14"}}})
        sid = self.chat(client, "你好").json()["session_id"]
        self.assertEqual(self.store.get_memory(user["id"])["facts"]["意向城市"]["value"], "杭州")
        state = self.store.one("SELECT state FROM chat_sessions WHERE id=?", (sid,))["state"]
        self.assertNotIn("杭州", state)

    def test_tenth_conversation_reminds_once(self):
        client = self.login()
        user = self.store.user_by_contact("13800001111")
        self.store.set_memory(user["id"], {"batches": [{"at": "10-14", "t": 1, "directions": ["A", "B", "C"]}]})
        texts = [self.chat(client, "你好").json()["text"] for _ in range(11)]  # 每次都是新对话
        reminded = [i for i, t in enumerate(texts) if "清理记忆" in t]
        self.assertEqual(reminded, [9])  # 第 10 个对话提醒，第 11 个不再提醒
        self.assertEqual(self.store.get_memory(user["id"])["reminded"], [10])

    def test_no_reminder_without_memory(self):
        client = self.login()
        texts = [self.chat(client, "你好").json()["text"] for _ in range(10)]
        self.assertFalse(any("清理记忆" in t for t in texts))


class SenderGateTests(unittest.TestCase):
    def test_prod_rejects_unimplemented_sender_name(self):
        # 写一个不存在的发送器名字不能骗过上线检查
        env = {"XIAOGU_ENV": "prod", "XIAOGU_SECRET": "s" * 32, "XIAOGU_ADMIN_TOKEN": "a" * 24, "XIAOGU_LOGIN_SENDER": "sms"}
        with self.assertRaises(SystemExit) as caught:
            webapp.Config(env)
        self.assertTrue("sms" in str(caught.exception) or "模拟数据" in str(caught.exception))


class OffTaskTests(PlatformCase):
    """10-14：简历美化、模拟面试、面试复盘暂时下线；后台开关打开就恢复。"""
    RESUME = ("张三\n手机：13812345678\n教育经历\n某某大学 统计学 本科 2022.09-2026.06\n"
              "项目经历\n课程推荐项目：用 Python 清洗选课日志\n实习经历\n某公司 数据分析实习生：整理周报数据")

    def test_mock_interview_is_off_by_default_without_charge(self):
        client = self.login()
        body = self.chat(client, "帮我模拟面试：推荐算法工程师").json()
        self.assertIn("还在打磨", body["text"])
        self.assertFalse(body["practice"]["active"])
        self.assertEqual(body["credits"]["charged"], 0)

    def test_resume_polish_is_off_but_resume_is_kept(self):
        client = self.login()
        body = self.chat(client, self.RESUME).json()
        self.assertIn("简历美化这个功能还在打磨", body["text"])
        self.assertIsNone(body.get("artifact"))
        self.assertEqual(self.platform.agent.sessions[body["session_id"]].resume, self.RESUME)

    def test_admin_flag_turns_interview_back_on(self):
        client = self.login()
        self.store.set_flag("task.interview", "1", "test")
        body = self.chat(client, "帮我模拟面试：推荐算法工程师").json()
        self.assertTrue(body["practice"]["active"])


class SmsSenderTests(unittest.TestCase):
    """阿里云短信（10-14 用户选定）：签名算法、只收手机号、生产配置检查。"""

    def test_signature_matches_aliyun_doc_example(self):
        from auth import aliyun_signature
        # 阿里云 RPC 签名 v1 官方文档示例（ECS DescribeRegions，AccessKeySecret=testsecret）
        params = {"AccessKeyId": "testid", "Action": "DescribeRegions", "Format": "XML", "SignatureMethod": "HMAC-SHA1",
                  "SignatureNonce": "3ee8c1b8-83d3-44af-a94f-4e0ad82fd6cf", "SignatureVersion": "1.0",
                  "Timestamp": "2016-02-23T12:46:24Z", "Version": "2014-05-26"}
        self.assertEqual(aliyun_signature(params, "testsecret"), "OLeaidS1JvxuMvnyHOwuJ+uX5qY=")

    def test_email_is_rejected_before_any_code(self):
        from auth import AliyunSmsSender, Auth, AuthError
        sent = []
        sender = AliyunSmsSender("id", "secret", "小谷求职", "SMS_1")
        sender.send = lambda contact, code: sent.append(contact)
        auth = Auth(Store(":memory:"), sender, "s")
        with self.assertRaises(AuthError) as caught:
            auth.request_code("someone@example.com")
        self.assertIn("手机号", str(caught.exception))
        auth.request_code("13800001111")
        self.assertEqual(sent, ["13800001111"])

    def test_prod_with_aliyun_needs_all_keys(self):
        env = {"XIAOGU_ENV": "prod", "XIAOGU_SECRET": "s" * 32, "XIAOGU_ADMIN_TOKEN": "a" * 24, "XIAOGU_LOGIN_SENDER": "aliyun"}
        with self.assertRaises(SystemExit) as caught:
            webapp.Config(env)
        self.assertIn("ALIYUN_SMS_ACCESS_KEY_ID", str(caught.exception))
        full = {**env, "ALIYUN_SMS_ACCESS_KEY_ID": "id", "ALIYUN_SMS_ACCESS_KEY_SECRET": "k",
                "ALIYUN_SMS_SIGN_NAME": "小谷求职", "ALIYUN_SMS_TEMPLATE_CODE": "SMS_1"}
        cfg = webapp.Config(full)  # 协议已定稿、模拟来源已去掉：齐了就能启动
        self.assertEqual(cfg.sender, "aliyun")
