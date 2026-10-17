# 追问时忘了已贴的招聘说明 · Debug 启动文档

## 元数据

- 日期：2026-10-11
- 任务名：同一会话贴过 JD 后，追问「接下来半年该怎么准备」却说「你没有提供具体岗位的招聘说明」
- 所属项目：xiaogu-launch（分支 launch-platform），web/agent.py
- 触发类型：debug（已触发 systematic-debugging）
- 关联 Principle：无（Principles 暂停）；关联笔记 notes/2026-10-05-direction-guidance-redesign.md（同类症状「招聘说明里没有提供具体信息」）

## 现象

第 1 轮贴 /Users/lucky_wang/Documents/Claude/projects/product-demo-video/videos/xiaogu-30s/rec/jd.txt（产品运营实习生），拆解正常（结论/依据/仍需确认/下一步）。
第 2 轮发「我是大三学生，想往这个方向走，接下来半年该怎么准备？」，回答开头「这是一般性建议，不来自小谷的资料库」，并说「因为你没有提供具体岗位的招聘说明…」。

## 复现

离线脚本（ScriptedProvider 记录提示词）：scratchpad/repro.py。第 2 轮被分类器判为 direction / general_advice / progress 任一时，模型收到的 user prompt 都是：

```
<evidence_pack>
（空）
（用户没有提供招聘说明：不要描述或评价任何“招聘说明”的内容，公司实际情况一律算未知）
</evidence_pack>
<known_facts>（无）</known_facts>
<dialogue>用户：【产品运营实习生】…（截到 300 字）</dialogue>
```

即服务端在提示词里明确告诉模型「用户没有提供招聘说明」，模型照做。

## 假设清单

1. 第 2 轮被路由到 career-master 聊天任务（direction/general/master/propose），这些任务调用 `_generate` 时证据包为空 `{}`。—— 成立（trace：route_by=llm，task=direction/general/master）。
2. `user_prompt` 以「证据包里有没有 J 编号」判断用户是否贴过 JD，而不看 `session.jd`。—— 成立，是根因。
3. session 没存住 JD（absorb 失败）。—— 排除：第 1 轮 stored=["job"]，session.jd 有值。
4. 模型无视了 dialogue 里的 JD 原文。—— 次要：dialogue 里确有 JD，但同一提示词里的明确否定句优先级更高；且 history 按 300 字截断，长 JD 会不全。
5. 第 1 轮拆解的「仍需确认」没有带到下一轮。—— 成立（session 不存），导致追问无法回扣开放问题。

## 已排除项

- JD 存储 / absorb 识别：正常。
- 分类器本身：判成 direction/general 合理（这是方向/准备类问题），问题不在分类。

## 根因

`web/agent.py` 的 `user_prompt()` 在证据包没有 J 编号时无条件追加「（用户没有提供招聘说明…）」。所有聊天任务都传空证据包，于是只要第 2 轮不走 suite，哪怕 `session.jd` 已存在，模型也被告知没有 JD。同一错误推断还存在于 `assemble()` 的 `JD_GENERALIZATION` 校验：它也按证据包判断「没贴 JD」，重写时的错误提示会再次告诉模型 user has not provided any 招聘说明。

## 修法

1. `user_prompt`：以 `session.jd` 为准。会话里有 JD 但本轮证据包没有 J 时，不写「没有提供」，改为附 `<job_description>`（完整 JD，当数据看）和 `<job_open_questions>`（上次拆解的仍需确认），并要求围绕该岗位职责作答、不要再让用户贴 JD。
2. `assemble`：新增 `has_jd` 参数，`JD_GENERALIZATION` 只在会话确实没有 JD 时生效。
3. `Session` 新增 `jd_unknowns`：suite + 本轮是 JD 时，存模型给的 unknown（不含服务端追加的从业者状态句）；贴新 JD 时清空重存。
4. 回归测试：tests/test_web_agent.py。

## 验证记录

- 回归测试（tests/test_web_agent.py，修复前 3 fail + 1 error，修复后通过）：
  - `test_followup_chat_after_jd_keeps_jd_and_open_questions`：direction / general_advice / progress 三种意图下，追问提示词不含旧的「（用户没有提供招聘说明：」，含完整 JD 和上轮开放问题，不含从业者来源状态句。
  - `test_chat_without_jd_still_says_no_jd`：没贴 JD 时旧约束仍在（保住 2026-10-05 的修复）。
  - `test_chat_mentioning_jd_is_not_rejected_when_jd_known`：会话有 JD 时，「这份招聘说明里一般……」不再被 JD_GENERALIZATION 打回（修复前耗尽预设输出、重写）。
- 全量：`XIAOGU_PROVIDER=mock .venv/bin/python -m unittest discover -s tests` → 120 tests OK。系统 python3 下 test_platform 因缺 httpx 导入失败，未改动的基线同样失败，与本次无关。
- 真实模型（deepseek-v4-pro 经 tornadorouter 中转，进程内两轮，不起服务、不占屏）：
  - 中转站样本 A（第 1 轮 blocked，jd_unknowns 为空；第 2 轮走 general）：回答围绕「社群运营 / 活动策划与复盘 / 对接设计研发」给半年准备，写「根据你贴的产品运营实习生招聘说明」，没有再说没提供 JD；首句仍是「这是一般性建议，不来自小谷的资料库」（general 任务既定要求）。因第 1 轮失败，这个样本不覆盖「回扣开放问题」。
  - 发现模型会照 phrasing.md 第 37 行自己写「从业者的实际说法：当前环境不能联网…」进 unknown，已改成按前缀过滤，测试已覆盖。
  - 中转站其余运行：多次 empty content / `Unterminated string`；第 1 轮也有 blocked（具体原因未抓到）；随后全部 HTTP 403，停止调用。
  - 官方端点样本 B（两轮都 complete，jd_unknowns 存下 4 条）：第 2 轮被分类器判成 job_understanding → suite → 把已存 JD 重新拆一遍，没回答「半年怎么准备」。没有出现「没提供 JD」，但也不满足预期。

## 遗留问题（未处理，待用户决定）

第 2 轮的意图分类不稳定：同一句在样本 A 判 general_advice，在样本 B 判 job_understanding。后者走 suite，沿用已存 JD 重做拆解（agent.py `_dispatch` 里「这个岗位加班多吗」那条沿用分支），绕开了本次修复的聊天路径。属于路由层的另一个问题。
