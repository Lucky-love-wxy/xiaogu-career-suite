"""小谷上线平台的数据层：用户、额度台账、模型调用、对话、埋点、开关。

设计见 notes/2026-10-05-launch-platform-design.md 第 4.2–4.7 节。
- 一期用 SQLite（WAL）：邀请制内测几十人，不需要单独的数据库服务；以后迁 Postgres 只换连接层。
- 余额不单独存，永远由 credit_ledger 求和得出；台账只追加不修改。
- 所有金额由这里的代码算，模型和前端都不参与。
"""

from __future__ import annotations

import json
import math
import re
import secrets
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

CN_TZ = timezone(timedelta(hours=8))  # 看板按北京时间切日
CREDITS_PER_CNY = 50  # 1 credit = ¥0.02：100 credits 对应后台 ¥2 实际消耗（10-14 用户定）
# 账本按 0.01 credit 记整数，界面显示两位小数（500.00 而不是 500）：按实际消耗扣，不再向上取整到 1 credit；
# 用整数而不是浮点，账目求和不会累积误差
UNITS = 100

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  contact TEXT UNIQUE NOT NULL,          -- 手机号或邮箱（登录凭证）
  status TEXT NOT NULL DEFAULT 'active', -- active / suspended：单用户停止开关
  invite_code TEXT,
  consent_at REAL NOT NULL,              -- 同意用户协议与隐私政策的时间
  theme TEXT NOT NULL DEFAULT 'mono',
  created_at REAL NOT NULL,
  last_seen REAL
);
CREATE TABLE IF NOT EXISTS invites (
  code TEXT PRIMARY KEY,
  credits INTEGER NOT NULL,
  max_uses INTEGER NOT NULL DEFAULT 1,
  used INTEGER NOT NULL DEFAULT 0,
  note TEXT,
  created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS login_codes (
  contact TEXT PRIMARY KEY,
  code_hash TEXT NOT NULL,
  expires_at REAL NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  sent_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS auth_tokens (
  token TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  expires_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS credit_ledger (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  type TEXT NOT NULL,      -- grant / consume / topup / refund / reserve / release / adjust
  credits INTEGER NOT NULL,-- 正数加、负数减
  ref TEXT,
  note TEXT,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ledger_user ON credit_ledger(user_id);
-- 基本情况卡片：每个用户一份，用户本人填写、随时可改可清空；不复制进会话状态（notes/2026-10-14-基本情况卡片与对话标注修复.md）
CREATE TABLE IF NOT EXISTS user_profile (
  user_id TEXT PRIMARY KEY,
  data TEXT NOT NULL,      -- JSON：字段见 agent.CARD_FIELDS
  updated_at REAL NOT NULL
);
-- 用户记忆文档：每个用户一份，跨对话记住说过的情况、给过的方向和反馈（notes/2026-10-14-用户记忆文档.md）。
-- 不给用户看、不做删除功能（10-14 用户定）；用户要求删除时由后台按 user_id 删行
CREATE TABLE IF NOT EXISTS user_memory (
  user_id TEXT PRIMARY KEY,
  data TEXT NOT NULL,      -- JSON：facts / batches / feedback / summary / reminded
  updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS chat_sessions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  title TEXT,
  state TEXT NOT NULL,     -- agent.Session 的 JSON，重启后恢复
  created_at REAL NOT NULL,
  updated_at REAL NOT NULL,
  deleted_at REAL          -- 用户删除：界面不再显示，6 个月后物理清除（日志留存要求）
);
CREATE INDEX IF NOT EXISTS ix_sessions_user ON chat_sessions(user_id);
CREATE TABLE IF NOT EXISTS turns (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  feature TEXT NOT NULL,   -- chat / resume / interview
  intent TEXT,
  status TEXT NOT NULL,    -- complete / needs_input / blocked / error / refused
  credits_charged INTEGER NOT NULL DEFAULT 0,
  cost_cny REAL NOT NULL DEFAULT 0,
  attempts INTEGER NOT NULL DEFAULT 0,
  ms INTEGER,
  user_message TEXT,
  final_text TEXT,
  created_at REAL NOT NULL,
  deleted_at REAL
);
CREATE INDEX IF NOT EXISTS ix_turns_user ON turns(user_id);
CREATE INDEX IF NOT EXISTS ix_turns_time ON turns(created_at);
CREATE TABLE IF NOT EXISTS llm_calls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  session_id TEXT,
  turn_id TEXT,
  model TEXT NOT NULL,
  prompt_tokens INTEGER NOT NULL,
  cache_hit_tokens INTEGER NOT NULL,
  completion_tokens INTEGER NOT NULL,
  cost_cny REAL NOT NULL,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_calls_time ON llm_calls(created_at);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT,
  name TEXT NOT NULL,
  props TEXT,
  env TEXT NOT NULL,
  created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_events_time ON events(created_at);
CREATE TABLE IF NOT EXISTS flags (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_by TEXT,
  updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS prices (
  model TEXT PRIMARY KEY,
  input_per_m REAL NOT NULL,      -- 元 / 百万 tokens，缓存未命中
  cache_hit_per_m REAL NOT NULL,  -- 元 / 百万 tokens，缓存命中
  output_per_m REAL NOT NULL,
  source TEXT,
  updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  cny REAL NOT NULL,
  credits INTEGER NOT NULL,
  status TEXT NOT NULL,     -- created / paid / refunded；二期接入支付后使用
  provider_trade_no TEXT,
  created_at REAL NOT NULL,
  paid_at REAL
);
"""

# 2026-10-05 取自 DeepSeek 官方价格页 https://api-docs.deepseek.com/zh-cn/quick_start/pricing
# 价格会变：以后台「单价」表为准，这里只是首次建库的初始值
DEFAULT_PRICES = {
    "deepseek-v4-pro": (3.0, 0.025, 6.0),
    "deepseek-v4-flash": (1.0, 0.02, 2.0),
    "mock": (0.0, 0.0, 0.0),
}

DEFAULT_FLAGS = {
    "maintenance": "0",                 # 全局停止：1 = 所有用户暂停使用
    "maintenance_reason": "",
    "feature.chat": "1",                # 单功能开关
    "feature.resume": "1",
    "feature.interview": "1",
    "task.polish": "0",                 # 整份简历美化：10-14 上线先关（还在打磨），后台可打开
    "task.interview": "0",              # 模拟面试 + 面试复盘：同上
    "signup_open": "1",                 # 是否允许新用户凭邀请码注册
    "markup": "1.0",                    # 用户扣费 = 成本 × 倍率；内测期 1.0 不赚钱
    "daily_cost_cap_cny": "50",         # 当日模型成本超过它自动全局停止
    "global_token_cap": "10000000",     # 全站累计 token（输入+输出，所有用户合计、不重置）用到它就全局停止；0 = 不限。与用户各自的 credits 无关
    "min_provider_balance_cny": "20",   # DeepSeek 账户余额低于它自动全局停止
    "min_provider_balance_usd": "3",    # 用 new-api 系中转站时：剩余额度（美元）低于它自动全局停止
}
FEATURES = ("chat", "resume", "interview")


def now() -> float:
    return time.time()


def day_start(days_ago: int = 0) -> float:
    """北京时间某天 0 点的时间戳。"""
    today = datetime.now(CN_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    return (today - timedelta(days=days_ago)).timestamp()


def mask(text: str | None) -> str:
    """后台展示用：手机号、邮箱、身份证号打码。对话正文里也可能出现，统一处理。"""
    if not text:
        return ""
    text = re.sub(r"(?<!\d)(1[3-9]\d)\d{4}(\d{4})(?!\d)", r"\1****\2", text)
    text = re.sub(r"(?<![\dXx])(\d{6})\d{8}(\d{3}[\dXx])(?![\dXx])", r"\1********\2", text)
    text = re.sub(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", r"\1***\2", text)
    return text


class Store:
    def __init__(self, path: Path | str, env: str = "dev"):
        self.path = str(path)
        self.env = env
        self._write = threading.Lock()  # SQLite 同时只有一个写者；预扣额度的“查余额+扣”必须原子
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._mem = sqlite3.connect(":memory:", check_same_thread=False) if self.path == ":memory:" else None
        with self.conn() as c:
            c.executescript(SCHEMA)
            if self.path != ":memory:":
                c.execute("PRAGMA journal_mode=WAL")
            if c.execute("PRAGMA user_version").fetchone()[0] < 1:
                # 2026-10-14：账本单位从 1 credit 改成 0.01 credit；旧数据按原 credit 数换算（不追溯汇率变化）
                c.execute("UPDATE credit_ledger SET credits = credits * 100")
                c.execute("UPDATE turns SET credits_charged = credits_charged * 100")
                c.execute("PRAGMA user_version = 1")
            for key, value in DEFAULT_FLAGS.items():
                c.execute("INSERT OR IGNORE INTO flags(key, value, updated_by, updated_at) VALUES (?,?,?,?)",
                          (key, value, "default", now()))
            for model, (i, h, o) in DEFAULT_PRICES.items():
                c.execute("INSERT OR IGNORE INTO prices VALUES (?,?,?,?,?,?)",
                          (model, i, h, o, "官方价格页 2026-10-05", now()))

    @contextmanager
    def conn(self) -> Iterator[sqlite3.Connection]:
        """每次操作开一个连接（测试用内存库时共用一个）。sqlite3 连接不跨线程共享。"""
        c = self._mem or sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            if self._mem is None:
                c.close()

    def rows(self, sql: str, args: tuple = ()) -> list[dict]:
        with self.conn() as c:
            return [dict(r) for r in c.execute(sql, args).fetchall()]

    def one(self, sql: str, args: tuple = ()) -> dict | None:
        found = self.rows(sql, args)
        return found[0] if found else None

    # ------------------------------------------------------------ 开关

    def flags(self) -> dict[str, str]:
        return {r["key"]: r["value"] for r in self.rows("SELECT key, value FROM flags")}

    def flag(self, key: str) -> str:
        row = self.one("SELECT value FROM flags WHERE key=?", (key,))
        return row["value"] if row else DEFAULT_FLAGS.get(key, "")

    def set_flag(self, key: str, value: str, by: str) -> None:
        if key not in DEFAULT_FLAGS:
            raise KeyError(key)
        with self._write, self.conn() as c:
            c.execute("INSERT INTO flags VALUES (?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
                      "updated_by=excluded.updated_by, updated_at=excluded.updated_at", (key, str(value), by, now()))

    # ------------------------------------------------------------ 用户与邀请码

    def create_invites(self, count: int, credits: int, max_uses: int = 1, note: str = "") -> list[str]:
        codes = []
        with self._write, self.conn() as c:
            for _ in range(count):
                code = secrets.token_hex(4).upper()  # 8 位，人能抄写
                c.execute("INSERT INTO invites VALUES (?,?,?,?,?,?)", (code, credits, max_uses, 0, note, now()))
                codes.append(code)
        return codes

    def user_by_contact(self, contact: str) -> dict | None:
        return self.one("SELECT * FROM users WHERE contact=?", (contact,))

    def user(self, user_id: str) -> dict | None:
        return self.one("SELECT * FROM users WHERE id=?", (user_id,))

    def register(self, contact: str, invite: str) -> dict:
        """凭邀请码注册并发放赠送额度。邀请码无效或用完抛 ValueError。"""
        invite = invite.strip().upper()
        with self._write, self.conn() as c:
            row = c.execute("SELECT * FROM invites WHERE code=?", (invite,)).fetchone()
            if not row or row["used"] >= row["max_uses"]:
                raise ValueError("邀请码无效或已用完")
            user_id = secrets.token_hex(8)
            c.execute("INSERT INTO users(id, contact, invite_code, consent_at, created_at) VALUES (?,?,?,?,?)",
                      (user_id, contact, invite, now(), now()))
            c.execute("UPDATE invites SET used = used + 1 WHERE code=?", (invite,))
            c.execute("INSERT INTO credit_ledger(user_id, type, credits, ref, note, created_at) VALUES (?,?,?,?,?,?)",
                      (user_id, "grant", row["credits"] * UNITS, invite, "注册赠送", now()))  # 邀请码上写的是 credit
        return self.user(user_id)

    def set_user_status(self, user_id: str, status: str) -> None:
        if status not in ("active", "suspended"):
            raise ValueError(status)
        with self._write, self.conn() as c:
            c.execute("UPDATE users SET status=? WHERE id=?", (status, user_id))

    def adjust_credits(self, user_id: str, credits: float, note: str) -> None:
        """后台手动加减额度（补偿、内测加额度），单位 credit，可带两位小数。"""
        with self._write, self.conn() as c:
            c.execute("INSERT INTO credit_ledger(user_id, type, credits, note, created_at) VALUES (?,?,?,?,?)",
                      (user_id, "adjust", round(credits * UNITS), note, now()))

    def touch(self, user_id: str) -> None:
        with self.conn() as c:
            c.execute("UPDATE users SET last_seen=? WHERE id=?", (now(), user_id))

    # ------------------------------------------------------------ 额度

    def balance(self, user_id: str) -> float:
        """余额，单位 credit，两位小数。"""
        row = self.one("SELECT COALESCE(SUM(credits),0) AS b FROM credit_ledger WHERE user_id=?", (user_id,))
        return row["b"] / UNITS

    def reserve(self, user_id: str, credits: float, minimum: float, ref: str) -> float:
        """预扣 min(credits, 余额)；余额低于 minimum 返回 0 表示不能开始。参数和返回值单位都是 credit。
        查余额和写预扣在同一把写锁里，同一用户开两个标签页也扣不成负数。本轮扣费不会超过预扣数。"""
        with self._write, self.conn() as c:
            bal = c.execute("SELECT COALESCE(SUM(credits),0) FROM credit_ledger WHERE user_id=?", (user_id,)).fetchone()[0]
            if bal < round(minimum * UNITS):
                return 0
            amount = min(round(credits * UNITS), bal)
            c.execute("INSERT INTO credit_ledger(user_id, type, credits, ref, created_at) VALUES (?,?,?,?,?)",
                      (user_id, "reserve", -amount, ref, now()))
        return amount / UNITS

    def settle(self, user_id: str, reserved: float, charge: float, ref: str) -> None:
        """结算：退回预扣，再按实际扣费（单位 credit）。charge 由调用方保证不超过 reserved。"""
        with self._write, self.conn() as c:
            c.execute("INSERT INTO credit_ledger(user_id, type, credits, ref, created_at) VALUES (?,?,?,?,?)",
                      (user_id, "release", round(reserved * UNITS), ref, now()))
            if charge:
                c.execute("INSERT INTO credit_ledger(user_id, type, credits, ref, created_at) VALUES (?,?,?,?,?)",
                          (user_id, "consume", -round(charge * UNITS), ref, now()))

    # ------------------------------------------------------------ 计量

    def price(self, model: str) -> tuple[float, float, float] | None:
        row = self.one("SELECT * FROM prices WHERE model=?", (model,))
        return (row["input_per_m"], row["cache_hit_per_m"], row["output_per_m"]) if row else None

    def call_cost(self, model: str, usage: dict) -> tuple[float, dict]:
        """按 DeepSeek usage 字段算一次调用的人民币成本。未知模型按最贵的已知单价算，宁可高估。"""
        prompt = int(usage.get("prompt_tokens") or 0)
        # DeepSeek 官方字段是 prompt_cache_hit_tokens；经 OpenAI 兼容中转站时可能只剩 prompt_tokens_details.cached_tokens
        hit = int(usage.get("prompt_cache_hit_tokens") or (usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
        out = int(usage.get("completion_tokens") or 0)
        price = self.price(model)
        if price is None:
            known = self.rows("SELECT input_per_m, cache_hit_per_m, output_per_m FROM prices")
            price = tuple(max(r[k] for r in known) for k in ("input_per_m", "cache_hit_per_m", "output_per_m"))
        cost = ((prompt - hit) * price[0] + hit * price[1] + out * price[2]) / 1_000_000
        return cost, {"prompt_tokens": prompt, "cache_hit_tokens": hit, "completion_tokens": out}

    def record_turn(self, turn: dict, calls: list[dict]) -> float:
        """写一轮对话和它的全部模型调用，返回本轮总成本（元）。"""
        total = 0.0
        with self._write, self.conn() as c:
            for call in calls:
                cost, tokens = self.call_cost(call["model"], call["usage"])
                total += cost
                c.execute("INSERT INTO llm_calls(user_id, session_id, turn_id, model, prompt_tokens, cache_hit_tokens, "
                          "completion_tokens, cost_cny, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                          (turn["user_id"], turn["session_id"], turn["id"], call["model"], tokens["prompt_tokens"],
                           tokens["cache_hit_tokens"], tokens["completion_tokens"], cost, now()))
            c.execute("INSERT INTO turns(id, user_id, session_id, feature, intent, status, credits_charged, cost_cny, "
                      "attempts, ms, user_message, final_text, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (turn["id"], turn["user_id"], turn["session_id"], turn["feature"], turn.get("intent"),
                       turn["status"], turn.get("credits_charged", 0), total, len(calls), turn.get("ms"),
                       turn.get("user_message"), turn.get("final_text"), now()))
        return total

    def set_turn_charge(self, turn_id: str, credits: float) -> None:
        with self.conn() as c:
            c.execute("UPDATE turns SET credits_charged=? WHERE id=?", (round(credits * UNITS), turn_id))

    def cost_since(self, since: float) -> float:
        row = self.one("SELECT COALESCE(SUM(cost_cny),0) AS s FROM llm_calls WHERE created_at>=?", (since,))
        return float(row["s"])

    def tokens_used(self) -> int:
        """全站累计消耗的 token（输入+输出），从第一次调用算起，不按周期清零。"""
        row = self.one("SELECT COALESCE(SUM(prompt_tokens + completion_tokens),0) AS s FROM llm_calls")
        return int(row["s"])

    def charge_for(self, cost_cny: float) -> float:
        """用户扣费：成本 × 倍率换成 credit，向上取到 0.01 credit（按实际消耗，不再取整到 1 credit）；成本为 0（模拟模型）不扣。"""
        if cost_cny <= 0:
            return 0
        markup = float(self.flag("markup") or 1)
        return max(1, math.ceil(cost_cny * CREDITS_PER_CNY * markup * UNITS - 1e-9)) / UNITS

    # ------------------------------------------------------------ 会话

    def session_owner(self, session_id: str) -> str | None:
        row = self.one("SELECT user_id FROM chat_sessions WHERE id=? AND deleted_at IS NULL", (session_id,))
        return row["user_id"] if row else None

    def load_session(self, session_id: str) -> dict | None:
        row = self.one("SELECT state FROM chat_sessions WHERE id=? AND deleted_at IS NULL", (session_id,))
        return json.loads(row["state"]) if row else None

    def get_profile(self, user_id: str) -> dict:
        row = self.one("SELECT data FROM user_profile WHERE user_id=?", (user_id,))
        return json.loads(row["data"]) if row else {}

    def set_profile(self, user_id: str, data: dict) -> None:
        """空卡片即清空：直接删行，不留旧内容。"""
        with self._write, self.conn() as c:
            if data:
                c.execute("INSERT INTO user_profile(user_id, data, updated_at) VALUES (?,?,?) "
                          "ON CONFLICT(user_id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
                          (user_id, json.dumps(data, ensure_ascii=False), now()))
            else:
                c.execute("DELETE FROM user_profile WHERE user_id=?", (user_id,))

    def get_memory(self, user_id: str) -> dict:
        row = self.one("SELECT data FROM user_memory WHERE user_id=?", (user_id,))
        return json.loads(row["data"]) if row else {}

    def set_memory(self, user_id: str, data: dict) -> None:
        with self._write, self.conn() as c:
            c.execute("INSERT INTO user_memory(user_id, data, updated_at) VALUES (?,?,?) "
                      "ON CONFLICT(user_id) DO UPDATE SET data=excluded.data, updated_at=excluded.updated_at",
                      (user_id, json.dumps(data, ensure_ascii=False), now()))

    def delete_memory(self, user_id: str) -> None:
        """用户要求删除时由后台调用（个人信息保护法第 47 条）；界面不提供。"""
        with self._write, self.conn() as c:
            c.execute("DELETE FROM user_memory WHERE user_id=?", (user_id,))

    def count_sessions(self, user_id: str) -> int:
        """用户开过的对话数（含已删除的）：10 个对话提醒清理记忆用。"""
        return self.one("SELECT COUNT(*) AS n FROM chat_sessions WHERE user_id=?", (user_id,))["n"]

    def save_session(self, session_id: str, user_id: str, state: dict, title: str) -> None:
        with self._write, self.conn() as c:
            c.execute("INSERT INTO chat_sessions(id, user_id, title, state, created_at, updated_at) VALUES (?,?,?,?,?,?) "
                      "ON CONFLICT(id) DO UPDATE SET state=excluded.state, updated_at=excluded.updated_at",
                      (session_id, user_id, title[:40], json.dumps(state, ensure_ascii=False), now(), now()))

    def list_sessions(self, user_id: str) -> list[dict]:
        return self.rows("SELECT id, title, updated_at FROM chat_sessions WHERE user_id=? AND deleted_at IS NULL "
                         "ORDER BY updated_at DESC LIMIT 50", (user_id,))

    def delete_session(self, user_id: str, session_id: str) -> bool:
        """用户删除对话：逻辑删除，界面和后台都不再展示；物理清除由 purge() 在 6 个月后做。"""
        with self._write, self.conn() as c:
            cur = c.execute("UPDATE chat_sessions SET deleted_at=? WHERE id=? AND user_id=? AND deleted_at IS NULL",
                            (now(), session_id, user_id))
            c.execute("UPDATE turns SET deleted_at=? WHERE session_id=? AND user_id=?", (now(), session_id, user_id))
        return cur.rowcount > 0

    def purge(self, older_than_days: int = 183) -> int:
        cutoff = now() - older_than_days * 86400
        with self._write, self.conn() as c:
            c.execute("DELETE FROM turns WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff,))
            return c.execute("DELETE FROM chat_sessions WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff,)).rowcount

    # ------------------------------------------------------------ 埋点

    def event(self, user_id: str | None, name: str, props: dict | None = None) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO events(user_id, name, props, env, created_at) VALUES (?,?,?,?,?)",
                      (user_id, name, json.dumps(props or {}, ensure_ascii=False)[:2000], self.env, now()))

    # ------------------------------------------------------------ 看板

    def dashboard(self, provider_balance: dict | None) -> dict[str, Any]:
        """后台看板的全部数字。毛利只算真实付费收入，赠送额度单列为获客成本。"""
        def window(since: float) -> dict:
            cost = self.cost_since(since)
            revenue = self.one("SELECT COALESCE(SUM(cny),0) AS s FROM orders WHERE status='paid' AND paid_at>=?", (since,))["s"]
            consumed = -self.one("SELECT COALESCE(SUM(credits),0) AS s FROM credit_ledger WHERE type='consume' AND created_at>=?",
                                 (since,))["s"]
            turns = self.one("SELECT COUNT(*) AS n, COUNT(DISTINCT user_id) AS u FROM turns WHERE created_at>=?", (since,))
            new_users = self.one("SELECT COUNT(*) AS n FROM users WHERE created_at>=?", (since,))["n"]
            return {"cost_cny": round(cost, 4), "revenue_cny": round(float(revenue), 2),
                    "gross_profit_cny": round(float(revenue) - cost, 4),
                    "credits_consumed": consumed / UNITS, "turns": turns["n"], "active_users": turns["u"], "new_users": new_users}

        granted = self.one("SELECT COALESCE(SUM(credits),0) AS s FROM credit_ledger WHERE type IN ('grant','adjust')")["s"]
        outstanding = self.one("SELECT COALESCE(SUM(credits),0) AS s FROM credit_ledger")["s"]
        users = self.rows("""
            SELECT u.id, u.contact, u.status, u.created_at, u.last_seen, u.invite_code,
              (SELECT COALESCE(SUM(credits),0) FROM credit_ledger l WHERE l.user_id=u.id) AS balance,
              (SELECT COALESCE(-SUM(credits),0) FROM credit_ledger l WHERE l.user_id=u.id AND l.type='consume') AS consumed,
              (SELECT COALESCE(SUM(cost_cny),0) FROM llm_calls c WHERE c.user_id=u.id) AS cost_cny,
              (SELECT COUNT(*) FROM turns t WHERE t.user_id=u.id) AS turns
            FROM users u ORDER BY u.last_seen DESC NULLS LAST, u.created_at DESC""")
        for u in users:
            u["contact"] = mask(u["contact"])
            u["cost_cny"] = round(u["cost_cny"], 4)
            u["balance"], u["consumed"] = u["balance"] / UNITS, u["consumed"] / UNITS
        since30 = day_start(29)
        features = self.rows("""
            SELECT feature, COUNT(*) AS turns, COUNT(DISTINCT user_id) AS users,
              AVG(cost_cny) AS avg_cost, SUM(cost_cny) AS cost,
              SUM(CASE WHEN status IN ('blocked','error') THEN 1 ELSE 0 END) AS failed
            FROM turns WHERE created_at>=? GROUP BY feature""", (since30,))
        quality = self.one("""
            SELECT COUNT(*) AS turns, AVG(attempts) AS avg_calls,
              SUM(CASE WHEN status='blocked' THEN 1 ELSE 0 END) AS blocked,
              SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) AS errors
            FROM turns WHERE created_at>=?""", (day_start(6),))
        latencies = [r["ms"] for r in self.rows("SELECT ms FROM turns WHERE created_at>=? AND ms IS NOT NULL ORDER BY ms",
                                                 (day_start(6),))]

        def pct(p: float):
            return latencies[min(len(latencies) - 1, int(len(latencies) * p))] if latencies else None

        daily = []
        for d in range(13, -1, -1):
            start, end = day_start(d), day_start(d - 1) if d else now() + 1
            cost = self.one("SELECT COALESCE(SUM(cost_cny),0) AS s FROM llm_calls WHERE created_at>=? AND created_at<?",
                            (start, end))["s"]
            n = self.one("SELECT COUNT(*) AS n, COUNT(DISTINCT user_id) AS u FROM turns WHERE created_at>=? AND created_at<?",
                         (start, end))
            daily.append({"day": datetime.fromtimestamp(start, CN_TZ).strftime("%m-%d"), "cost_cny": round(cost, 4),
                          "turns": n["n"], "users": n["u"]})
        top_events = self.rows("SELECT name, COUNT(*) AS n FROM events WHERE created_at>=? GROUP BY name ORDER BY n DESC",
                               (day_start(6),))
        return {
            "env": self.env,
            "generated_at": now(),
            "provider_balance": provider_balance,
            "tokens": {"used": self.tokens_used(), "cap": int(float(self.flag("global_token_cap") or 0))},
            "liability": {"credits_outstanding": outstanding / UNITS, "cny_outstanding": round(outstanding / UNITS / CREDITS_PER_CNY, 2),
                          "credits_granted_total": granted / UNITS},
            "today": window(day_start(0)), "d7": window(day_start(6)), "d30": window(since30),
            "daily": daily,
            "users": users,
            "features": [{**f, "avg_cost": round(f["avg_cost"] or 0, 4), "cost": round(f["cost"] or 0, 4)} for f in features],
            "quality": {**quality, "avg_calls": round(quality["avg_calls"] or 0, 2), "p50_ms": pct(0.5), "p95_ms": pct(0.95)},
            "events": top_events,
            "flags": self.flags(),
            "prices": self.rows("SELECT model, input_per_m, cache_hit_per_m, output_per_m, source FROM prices ORDER BY model"),
            "recent": self.recent_activity(),
            "invites": self.rows("SELECT code, credits, max_uses, used, note, created_at FROM invites ORDER BY created_at DESC LIMIT 50"),
        }

    def recent_activity(self, limit: int = 20) -> dict[str, list[dict]]:
        """后台「实时」：所有用户最近的对话和埋点事件，按时间倒序。联系方式和正文打码，正文只取开头。"""
        turns = self.rows("""
            SELECT t.created_at, u.contact, t.feature, t.status, t.credits_charged / 100.0 AS credits_charged, t.cost_cny, t.ms, t.user_message
            FROM turns t LEFT JOIN users u ON u.id = t.user_id ORDER BY t.created_at DESC LIMIT ?""", (limit,))
        for t in turns:
            t["contact"] = mask(t["contact"])
            t["user_message"] = mask((t["user_message"] or "")[:80])
            t["cost_cny"] = round(t["cost_cny"], 5)
        events = self.rows("""
            SELECT e.created_at, e.name, e.props, u.contact FROM events e LEFT JOIN users u ON u.id = e.user_id
            ORDER BY e.id DESC LIMIT ?""", (limit,))
        for e in events:
            e["contact"] = mask(e["contact"])
        return {"turns": turns, "events": events}

    def user_turns(self, user_id: str, limit: int = 100) -> list[dict]:
        """后台查看某用户的对话（含已被用户删除但仍在留存期的，标记出来）。联系方式和证件号打码。"""
        rows = self.rows("SELECT id, session_id, feature, intent, status, credits_charged / 100.0 AS credits_charged, cost_cny, attempts, ms, "
                         "user_message, final_text, created_at, deleted_at FROM turns WHERE user_id=? "
                         "ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        for r in rows:
            r["user_message"], r["final_text"] = mask(r["user_message"]), mask(r["final_text"])
            r["cost_cny"] = round(r["cost_cny"], 5)
        return rows
