# 零基础使用与输出格式验收 · 2026-10-01

## 结论

33 项本地行为测试通过，6 项独立新会话的真实 Codex CLI Agent 试用通过。用户只输入日常中文，不指定 Skill，不运行命令，不编辑 JSON。独立只读审阅的 Important 已修复，复核 PASS。

这是虚构材料和新手措辞的模拟验收，不是零基础真人观察实验，也不是 WorkBuddy GUI 验收。测试使用本机已有 Codex CLI 默认模型（首轮显示 gpt-6.1-sol），其他主机或模型需重新验证。Skill 指令不能保证所有主机永久遵守格式，当前未实现主机级输出拦截。

## 真实 Agent 用例

| 场景 | 结果 | 本地证据目录名 |
|---|---|---|
| 首次使用，无方向 | PASS | `xiaogu-acceptance-608v239b` |
| 改简历但没有材料 | PASS | `xiaogu-acceptance-0ntku1rm` |
| 扁平化管理 | PASS | `xiaogu-acceptance-v50ns70h` |
| 20K、14薪、假期、周末会议和团建 | PASS | `xiaogu-acceptance-a_xp25d9` |
| 课程项目生成岗位版简历 | PASS | `xiaogu-acceptance-gde7ybqf` |
| 回忆问答复盘，无JD和录音 | PASS | `xiaogu-acceptance-ou5_kdlr` |

完整本地证据位于 `evidence/beginner-acceptance-2026-10-01/`，每项含 trace.jsonl、final.md、result.json。证据与临时运行日志不进入 Git 或分发包；公开可复现的虚构输入在 `scripts/run_agent_acceptance.py`。

验收条件：运行成功、调用渲染器成功、从实际 response.json 独立渲染后与最终消息逐字一致、没有向用户暴露命令/JSON编辑要求。另人工检查内容：待遇没有把额外两薪当保底、保留双休与周六会议的冲突；简历没有补造上线或性能数字；复盘把回忆标为本人提供记录，练习方案不写成已有经历。

## 发现与修复

- 日常说法：招聘说明、第一次用AI、刚面试完，以及全部61个词条进入对应功能。
- 短材料：一题明确问答也可先分析，不以字数代替是否有材料。
- 背景与动作：投递没回复不会抢占后续招聘说明、黑话、面试或外部调研请求；也不擅自认定简历是原因。
- 独立安装：简历、面试复盘各自包含校验器，不依赖不存在的上级目录。
- 薪数空格：14 薪能匹配，保留输入原句。
- 输出：固定结论、依据、仍需确认、下一步的按需顺序，常见内部字段泄漏和多个问号会被拒绝。单问语义仍由Agent指令约束，不声称算法能识别所有多项索取。
- 测试脚本：合并shell命令的文件创建提示导致初次格式误判；改为读取实际JSON独立渲染，并新增防误判回归。

## 未通过的界面验收与未覆盖范围

WorkBuddy 5.6.2 可读取旧会话，但截图/交互报 `ScreenCaptureKit SCStreamErrorDomain -3812 参数无效`，无法完成新会话试用。现有安装还显示旧词库和缺少面试复盘 Skill。未清空账号、未改用户历史或其他设置。需恢复桌面界面控制后，安装本版四个 Skill 并用以上同一输入复测。

未测试：真人理解程度、WorkBuddy隐式发现和跨轮材料继承、BOSS账号登录与真实岗位检索、外部帖子访问，以及具体公司福利兑现。不能由本次通过推断这些能力已验收。

## 复现与修改地图

本地：`python3 -m unittest discover -s tests`。
真实Agent：`python3 scripts/run_agent_acceptance.py --case benefits --execute --codex /绝对路径/codex`。默认不加 --execute 只预览。CLI需要本机已有认证，使用已有默认模型和虚构输入。

- 路由：`skills/xiaogu-career-master/scripts/route_request.py` 与词条路由索引。
- 输出：master SKILL.md、references/output-contract.md、scripts/render_response.py。
- 解释：core scripts/search.py 与 scripts/xiaogu_search.py。
- 简历/复盘：各自 SKILL.md、scripts/validate_*.py 和内置 validate_artifact.py。
- 测试：tests/test_beginner_acceptance.py、scripts/run_agent_acceptance.py。
- 新手说明：docs/workbuddy/一句话使用小谷.md。
- 包装：scripts/package.py；产物 dist/xiaogu-career-suite-v2.4.zip。
