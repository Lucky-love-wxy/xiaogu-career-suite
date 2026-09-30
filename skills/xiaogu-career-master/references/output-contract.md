# 小谷用户可见输出契约

此契约是 Harness 最终输出的统一外壳，不替代各 Skill 的详细分析产物。当前自动化测试已经覆盖路由、JD 事实边界和复盘产物校验；此前没有用户可见格式测试，因此本契约只固定可验证的输出顺序和证据标签，不声称 WorkBuddy 界面已验证。

## 内部结构

执行业务 Skill 后，Harness 整理为 JSON，再运行 `python3 scripts/render_response.py response.json`。只有命令成功时才发送其 Markdown 输出。结构：

```json
{
  "status": "complete",
  "answer": "一句话结论，可用简短换行展开必要细节",
  "evidence": [{"kind": "jd_fact", "text": "可追溯的原句或事实"}],
  "unknown": ["材料尚未说明的关键条件"],
  "next_action": "一个最有价值的动作，或 null"
}
```

`kind` 只允许 `jd_fact`、`offer_fact`、`transcript_fact`、`candidate_confirmed`、`reference`、`external_report`、`inference`。证据项不得把匿名评价写成已核实的公司事实；`inference` 始终标为待核实。没有实际依据时 `evidence` 用空列表，不能凑来源。

需要材料时：`{"status":"needs_input","question":"请粘贴……？"}`，只发这一个问题。执行受阻时还需 `blocker`，具体说明失败步骤和原因；已有结果仍放在 `answer`。`unknown` 必须是列表；`next_action` 只允许一行字符串或 `null`。

## 用户看到的格式

正常完成依次显示：**结论**、有证据时的**依据**、有缺口时的**仍需确认**、确需用户行动时的**下一步**。缺材料只显示一个问题；受阻时在依据之后加**受阻原因**。不展示路由、JSON、脚本或内部阶段名。

各场景的 `answer` 内容由业务 Skill 决定：黑话解释保留字面、实际含义与风险条件；待遇解释列清固定现金和条件收入；面试复盘保留前三项优先改进与逐题定位。结构化事实源和详细复盘存入产物，不为了填四段文字而丢掉逐题证据。

不得输出虚构薪资、录用概率或招聘方未承诺的福利。没有 JD 时可以做一般解释，但要在 `unknown` 明确缺少目标公司材料。
