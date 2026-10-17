import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))
import agent  # noqa: E402

rt, iv = agent.rt, agent.iv
JD = (ROOT / "examples" / "algorithm-engineer-mock" / "jd.txt").read_text(encoding="utf-8")
RESUME = """张三
手机：13812345678  邮箱：zhangsan@example.com
教育经历
某某大学 统计学 本科 2022.09-2026.06
项目经历
课程推荐项目：参与用 Python 清洗选课日志，用 LightGBM 做排序，离线 AUC 从 0.71 提升到 0.76
实习经历
某公司 数据分析实习生 2025.07-2025.09：负责整理周报数据，用 SQL 取数
"""


def structured(bullets, name="张三", **extra):
    return json.dumps({"basics": {"name": name, "phone": "13900000000"},
                       "sections": [{"key": "projects", "title": "项目经历", "items": [{"title": "课程推荐项目", "bullets": bullets}]},
                                    {"key": "education", "title": "教育经历", "items": [{"title": "某某大学", "date": "2022.09-2026.06"}]}],
                       "changes": ["统一了写法"], **extra}, ensure_ascii=False)


class Scripted:
    """按顺序返回预设输出；分类器调用不消耗预设。"""
    name, model = "scripted", "scripted"

    def __init__(self, outputs, intent="direction"):
        self.outputs, self.intent, self.prompts = list(outputs), intent, []

    def complete(self, messages):
        if "意图分类器" in messages[0]["content"]:
            return json.dumps({"intent": self.intent, "role": None})
        self.prompts.append(messages[-1]["content"])
        return self.outputs.pop(0)


class ResumeToolTests(unittest.TestCase):
    def test_chinese_keyword_matches_inside_sentence_and_ascii_keeps_word_boundary(self):
        self.assertTrue(rt.keyword_hit("数据分析", "负责数据分析工作"))
        self.assertFalse(rt.keyword_hit("Java", "熟悉 JavaScript"))
        self.assertTrue(rt.keyword_hit("python", "用 Python 写脚本"))
        self.assertEqual(rt.coverage(["Python", "Hive"], "用 Python")["percent"], 50)
        self.assertEqual(rt.coverage([], "任何文本")["percent"], 0)

    def test_novel_numbers_ignore_dates_and_existing_values(self):
        self.assertEqual(rt.novel_numbers(RESUME, "离线 AUC 提升到 0.76，2022.09-2026.06"), [])
        self.assertEqual(rt.novel_numbers(RESUME, "效率提升 30%"), ["30%"])
        self.assertEqual(rt.novel_numbers(RESUME, "服务 2 万用户"), ["2万"])

    def test_faithful_check_rejects_new_tools_and_role_upgrade(self):
        resume, errors = rt.normalize(json.loads(structured(["主导用 Spark 清洗选课日志"])), RESUME)
        self.assertEqual(errors, [])
        problems = " ".join(rt.faithful_errors(resume, RESUME))
        self.assertIn("Spark", problems)
        self.assertIn("主导", problems)

    def test_invented_role_on_project_is_rejected(self):
        data = json.loads(structured(["参与用 Python 清洗选课日志"]))
        data["sections"][0]["items"][0]["subtitle"] = "产品实习生"
        resume, _ = rt.normalize(data, RESUME)
        self.assertTrue(any("产品实习生" in e for e in rt.faithful_errors(resume, RESUME)))

    def test_contacts_come_from_original_text_not_model(self):
        resume, _ = rt.normalize(json.loads(structured(["参与用 Python 清洗选课日志"], name="李四")), RESUME)
        self.assertEqual(resume["basics"]["phone"], "13812345678")  # 模型给的 139 号码被原文覆盖
        self.assertEqual(resume["basics"]["email"], "zhangsan@example.com")
        self.assertEqual(resume["basics"]["name"], "")  # 原文里没有“李四”，不采用
        self.assertEqual([s["key"] for s in resume["sections"]], ["education", "projects"])  # 学生版顺序

    def test_render_escapes_user_content(self):
        resume, _ = rt.normalize(json.loads(structured(["<script>alert(1)</script>"])), RESUME + "<script>alert(1)</script>")
        page = rt.render_html(resume, "通用版")
        self.assertNotIn("<script>alert", page)
        self.assertIn("&lt;script&gt;", page)

    def test_resume_detection(self):
        self.assertTrue(rt.looks_like_resume(RESUME))
        self.assertFalse(rt.looks_like_resume(JD))
        self.assertFalse(rt.looks_like_resume("我做过一个课程推荐项目，负责清洗数据。"))


class ResumeFlowTests(unittest.TestCase):
    def test_pasted_resume_does_not_overwrite_saved_jd(self):
        a = agent.Agent(agent.MockProvider())
        sid = a.handle(None, "帮我看看这个岗位：\n" + JD)["session_id"]
        a.handle(sid, RESUME)
        self.assertEqual(a.sessions[sid].jd, "帮我看看这个岗位：\n" + JD)
        self.assertEqual(a.sessions[sid].resume, RESUME)

    def test_polish_retries_when_model_invents_numbers_and_returns_artifact(self):
        provider = Scripted([structured(["参与清洗选课日志，效率提升 30%"]), structured(["参与用 Python 清洗选课日志"])])
        a = agent.Agent(provider)
        result = a.handle(None, RESUME)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(len(provider.prompts), 2)
        self.assertIn("没有通过校验", provider.prompts[1])  # 第二次是带着错误原因重写
        self.assertTrue(any("30%" in str(e) for e in result["trace"]["attempts"][0]))
        self.assertTrue(result["artifact"]["url"].startswith("/resume/"))
        self.assertTrue(result["trace"]["beta"])  # 贝塔功能，前端据此标注
        self.assertIn("beta 版", a.artifact(result["artifact"]["url"].rsplit("/", 1)[-1]))
        self.assertIn("课程推荐项目", a.artifact(result["artifact"]["url"].rsplit("/", 1)[-1]))

    def test_tailor_reports_coverage_computed_by_code_and_drops_invented_keywords(self):
        keywords = json.dumps({"required_skills": ["Python", "C++", "Kubernetes"], "keywords": ["推荐系统"]}, ensure_ascii=False)
        provider = Scripted([keywords, structured(["参与用 Python 清洗选课日志，用 LightGBM 做排序"])], intent="resume_for_job")
        a = agent.Agent(provider)
        session = a.session(None)
        session.jd, session.resume, session.experience = JD, RESUME, RESUME
        result = a.handle(session.id, "帮我按这个岗位改简历")
        self.assertEqual(result["status"], "complete")
        cov = result["trace"]["coverage"]
        self.assertNotIn("Kubernetes", JD)
        self.assertEqual(cov["keywords"], 3 if "推荐系统" in JD else 2)  # JD 里没有的词被丢掉
        self.assertIn("改前", result["text"])
        self.assertIn("不代表能不能通过筛选", result["text"])
        self.assertIn("C++", result["text"])  # 找不到依据的要求进“仍需确认”


class PracticeTests(unittest.TestCase):
    def start(self):
        a = agent.Agent(agent.MockProvider())
        sid = a.handle(None, RESUME)["session_id"]
        result = a.handle(sid, "帮我模拟面试")
        return a, sid, result

    def test_practice_flow_follow_up_give_up_and_score(self):
        a, sid, result = self.start()
        self.assertTrue(result["practice"]["active"])
        self.assertIn("第 1 题", result["text"])
        r = a.handle(sid, "我负责用 Python 清洗日志，写了去重脚本。")
        self.assertIn("追问", r["text"])
        self.assertEqual(a.sessions[sid].experience, RESUME)  # 回答没有覆盖经历
        a.handle(sid, "因为原始日志有重复记录。")
        r = a.handle(sid, "不知道")
        self.assertIn("第 3 题", r["text"])  # 放弃作答不追问
        r = a.handle(sid, "结束")
        self.assertFalse(r["practice"]["active"])
        self.assertEqual(r["trace"]["practice_score"]["per_question"], [60, 0])
        self.assertIn("综合 30 分", r["text"])
        self.assertIn("面试官问", a.sessions[sid].transcript)
        review = a.handle(sid, "复盘这场面试")
        self.assertIn("xiaogu-interview-review", review["trace"]["route"]["pipeline"])

    def test_give_up_only_when_whole_answer_is_giving_up(self):
        for text in ["不知道", "这题我真的不会。", "忘了"]:
            self.assertTrue(iv.is_give_up(text), text)
        for text in ["不会，我会先跟研发对齐", "这种情况不会出现", "这个我没做过，但会先查资料"]:
            self.assertFalse(iv.is_give_up(text), text)
        for text in ["结束", "结束吧", "好了结束", "不练了。"]:
            self.assertTrue(iv.END.match(text), text)
        self.assertFalse(iv.END.match("结束之后我会复盘数据"))

    def test_resume_question_must_cite_candidate_evidence(self):
        bank = {"directions": [], "questions": [
            {"type": "resume", "level": lv, "topic": "t", "question": "q？", "follow_up": "f？", "basis": "", "key_points": ["p"]}
            for lv in ["基础", "基础", "进阶", "进阶", "深入"]]}
        _, errors = iv.validate_bank(bank, {"C1"}, has_jd=False)
        self.assertTrue(any("must cite a C id" in e for e in errors))

    def test_overall_score_is_weighted_by_code(self):
        items, _, errors = iv.score_items({"items": [{"n": 1, "accuracy": 100, "completeness": 0, "depth": 0, "expression": 0,
                                                       "feedback": "x"}]}, 1)
        self.assertEqual(errors, [])
        self.assertEqual(items[0]["score"], 40)

    def test_practice_without_any_material_asks_for_role_then_starts(self):
        a = agent.Agent(agent.MockProvider())
        r = a.handle(None, "帮我模拟面试")
        self.assertEqual(r["status"], "needs_input")
        r = a.handle(r["session_id"], "产品经理")
        self.assertTrue(r["practice"]["active"])
        self.assertIn("产品经理", r["text"])


class InterviewApiTests(unittest.TestCase):
    """语音前端用的纯文本接口：重复 start、先问岗位再 answer 两条路径。"""

    def setUp(self):
        import server
        server.Handler.xiaogu = agent.Agent(agent.MockProvider())
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()

    def post(self, path, body):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as res:
                return res.status, json.load(res)
        except urllib.error.HTTPError as exc:
            with exc:
                return exc.code, json.load(exc)

    def test_start_without_material_then_answer_role(self):
        status, r = self.post("/api/interview/start", {})
        self.assertEqual((status, r["status"]), (200, "needs_input"))
        status, r = self.post("/api/interview/answer", {"session_id": r["session_id"], "text": "产品经理"})
        self.assertEqual(status, 200)
        self.assertTrue(r["practice"]["active"])

    def test_second_start_during_interview_is_rejected_not_recorded(self):
        status, r = self.post("/api/interview/start", {"role": "产品经理"})
        sid = r["session_id"]
        status, again = self.post("/api/interview/start", {"session_id": sid, "role": "产品经理"})
        self.assertEqual(status, 409)
        self.assertEqual(server_log(sid), [])

    def test_resume_page_is_served(self):
        status, r = self.post("/api/chat", {"message": RESUME})
        with urllib.request.urlopen(self.base + r["artifact"]["url"]) as res:
            self.assertIn("课程推荐项目".encode(), res.read())


def server_log(sid):
    import server
    return server.Handler.xiaogu.sessions[sid].practice["log"]


if __name__ == "__main__":
    unittest.main()
