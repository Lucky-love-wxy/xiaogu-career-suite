"""求职进度看板（测试版）的汇总逻辑：漏斗逐段点亮、计划进度、7 天没动静提醒。纯函数，方便测试。
设计见 notes/2026-10-17-求职进度看板与校招日历.md（用户 10-17 定：五段、7 天算没动静）。"""

from __future__ import annotations

import time

STAGES = ("want", "applied", "test", "interview", "offer")
STAGE_LABEL = {"want": "想投", "applied": "已投递", "test": "测评/笔试", "interview": "面试", "offer": "offer"}
OUTCOMES = ("rejected", "no_reply")
STALE_DAYS = 7
# 对话里提到这些反馈时，看板新增或推进一条（memory 的 feedback 类别 → 阶段）
FEEDBACK_STAGE = {"投了": "applied", "有面试": "interview", "拿到offer": "offer"}


def summarize(plan: dict | None, apps: list[dict], now: float | None = None) -> dict:
    """漏斗按“到达过这一段”累计：在面试阶段的投递也算点亮了已投递和测评。被拒、无回音的停在当时阶段。"""
    now = now or time.time()
    reached = {s: 0 for s in STAGES}
    for app in apps:
        idx = STAGES.index(app["stage"]) if app["stage"] in STAGES else 0
        for s in STAGES[: idx + 1]:
            reached[s] += 1
    applied = reached["applied"]  # 想投的不算已投
    stale = [a["id"] for a in apps
             if a["stage"] == "applied" and not a.get("outcome") and now - a["stage_at"] >= STALE_DAYS * 86400]
    target = (plan or {}).get("target_count") or 0
    return {
        "stages": [{"key": s, "label": STAGE_LABEL[s], "count": reached[s], "lit": reached[s] > 0} for s in STAGES],
        "plan": plan,
        "plan_progress": {"applied": applied, "target": target, "percent": round(applied / target * 100) if target else None},
        "active": sum(1 for a in apps if not a.get("outcome") and a["stage"] != "offer"),
        "rejected": sum(1 for a in apps if a.get("outcome") == "rejected"),
        "no_reply": sum(1 for a in apps if a.get("outcome") == "no_reply"),
        "stale": stale,
    }


def apply_feedback(store, user_id: str, items: list[dict]) -> list[str]:
    """对话里新出现的“投了 / 有面试 / 拿到offer”：说了公司名才记。已有同公司的记录就推进阶段（只进不退），没有就新增。
    返回本轮记下的公司名，用来在回复末尾说一句。"""
    noted = []
    apps = store.list_applications(user_id)
    for item in items:
        stage, company = FEEDBACK_STAGE.get(item.get("kind")), (item.get("company") or "").strip()[:40]
        if not stage or not company:
            continue
        match = next((a for a in apps if a["company"] == company and not a.get("outcome")), None)
        if match:
            if STAGES.index(stage) > STAGES.index(match["stage"]):
                store.update_application(user_id, match["id"], {"stage": stage})
                match["stage"] = stage
                noted.append(company)
        else:
            store.add_application(user_id, company, (item.get("role") or "").strip()[:40], stage=stage, source="chat")
            apps = store.list_applications(user_id)
            noted.append(company)
    return noted
