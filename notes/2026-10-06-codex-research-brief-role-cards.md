# Codex 调研 Brief：岗位卡片（每个岗位到底在做什么）

- 下发日期：2026-10-06
- 设计方：Claude（顶层设计）；执行方：Codex
- 上游文档：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/notes/2026-10-05-career-db-v2.md（第 7 节：提问树）
- 待调研岗位清单：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/research_queue.csv（170 个岗位，分 P1/P2/P3）
- 交付落点：
  - 岗位卡片：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/role_cards/<岗位id>.json（一个岗位一个文件）
  - 汇总报告：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/docs/research/role-cards-2026-10.md
  - 脚本：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/scripts/rolecards/
  - 原始证据：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/evidence/role-cards-2026-10/（evidence/ 已在 .gitignore）
  - 恢复入口：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/tasks/research-2026-10/start.md 追加一节

## 背景

职业库 v2 已经解决“尽可能广”：BOSS 分类树 1098 个末级岗位 + 牛企直聘校招单岗样本 2723 条 + 人工核实 28 份，专业 → 岗位连线 892 条。现在进入“精准”阶段：小谷按提问树逐层问用户，走到最末一层时要能用人话说清这个岗位每天在做什么、交付什么、和谁打交道、新人怎么进、常见误解是什么。目前库里每个岗位只有样本数、学历分布和两三句招聘原文职责，不够。

用户 2026-10-06 的范围决定：
- 医院/学术路线（医生、护士、医技等，提问树 A 支）不调研：路径由考试、规培、考研决定，相对固定，与小谷“按招聘说明改简历”的核心关系不大。research_queue.csv 已排除这些岗位。
- 先做医院外的医学相关岗位（P1，50 个），再做通用岗位（P2，45 个），P3（75 个，单家单位样本）最后、可部分完成。

## 每个岗位要回答的问题（岗位卡片字段）

字段对齐现有职业索引契约 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/skills/xiaogu-career-suite/references/index-contract.md，并加两个本次需要的字段：

| 字段 | 内容 | 主要依据 |
|---|---|---|
| name / aliases | 标准名 + 招聘里的真实写法（从样本标题统计） | 招聘样本 |
| plain_language | 一句人话：这个岗位在干什么 | 多来源综合 |
| daily_work | 日常任务 4–8 条，具体动作 | 招聘职责高频句 + 从业者分享 |
| deliverables | 交付物（报告、病例报告表、注册资料……） | 同上 |
| collaborators | 主要和谁打交道（医生、患者、药企、监管部门……） | 同上 |
| work_setting | 工作场景：是否常驻医院/出差/坐班/实验室 | 招聘原文 + 从业者分享 |
| entry_for_fresh | 应届生怎么进：常见学历、专业、是否接受无经验、常见证书 | 只用计数（例如“12 份校招样本中 9 份写本科”），不写“通常” |
| metrics | 常见考核指标 | 从业者分享；没有就留空 |
| growth | 常见发展路径 | 从业者分享；没有就留空 |
| risks / misconceptions | 新手常见误解和条件化风险（写成“如果……则……”） | 从业者分享 |
| questions | 面试或问招聘方时该核实的 3 个问题 | 由上面的缺口推出，标为“建议问题” |
| search_keywords | 在招聘平台搜这个岗位的关键词 | 样本标题统计 |
| evidence | 每条结论对应的来源：类型、标题、URL、日期、适用范围 | — |

每个字段里的每条陈述都要能指到 evidence 中的至少一条；指不到就不写。

## 证据标准

1. 来源等级沿用索引契约：多名从业者独立分享 > 单名从业者具体经历 > 媒体或课程机构转述 > 招聘 JD（只证明雇主要求，不证明实际体验）。
2. 每张卡片至少：招聘样本 ≥ 3 份（来自库内或新补），从业者一手分享 ≥ 2 条（不同作者）。达不到就标 `evidence_level: partial`，并在卡片里写清缺什么。
3. 允许的从业者来源：牛客公开帖子、知乎专栏的公开文章页（先核实 robots 对具体路径是否放行）、公司官网职业介绍、行业协会或监管机构公开文件（例如 GCP、药物警戒质量管理规范这类规定岗位职责的官方文件）。不碰脉脉；不使用登录态；不绕验证码；单站请求间隔 ≥ 3 秒（牛企直聘按其 robots 为 4 秒）。
4. 帖子只复述要点，引用原文单处不超过 30 字；不保存作者昵称以外的个人信息。
5. 发帖日期必须记录；3 年以前的分享只能作为“当时的情况”。
6. 查不到写“未找到”，不用常识补齐；厂商宣传和实际观察分开写。

## 脚本辅助（岗位量大，必须用脚本，不要逐个手工读）

建议的流水线，具体实现由你判断：

1. **聚合已有样本**（不联网）：读 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/postings_mapped.jsonl 与 postings.jsonl，按岗位节点汇总职责原文、任职要求、学历、专业、标题写法；统计高频动作短语（动词 + 宾语）和高频要求。输出每个岗位的“样本摘要”文件，作为写卡片的第一手材料。注意职责句里混有薪资、单位名、日期，需要过滤（可参考 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/scripts/careerdb/build.py 的 duty_lines）。
2. **补招聘样本**（联网，低频）：样本 < 3 份的岗位，用 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/scripts/careerdb/crawl.py 同样的方式（牛企直聘站内搜索第一页，Crawl-delay 4）补抓；不翻页（robots 禁止 ?Page=）。
3. **找从业者分享**（联网，低频）：按岗位名 + “日常/一天/工作内容/面经”等组合在允许的来源发现公开帖子，保存原文页面与访问日期到 evidence 目录；每个岗位最多取 10 条候选，再人工或半自动筛出 2–5 条真正讲工作内容的。
4. **起草卡片**：可以用模型从“样本摘要 + 帖子要点”起草，但必须带引用编号，起草后由脚本逐条核验：每条陈述引用的 evidence 存在；引用的原文片段在保存的页面里逐字出现；数字在样本里可复算。核验不过的条目删除，不改写成更模糊的说法。
5. **抽查**：每 20 张卡片人工通读 3 张，记录发现的问题并回改脚本。

先做试点：P1 里挑 5 个差异大的岗位（建议：临床协调员、医学事务/医学信息、药物警戒、医学理赔/核保、医学AI/生物医学大模型），跑通流水线、交一版报告，再批量推进。

## 交付与验收

- [ ] 试点 5 张卡片 + 流水线脚本，先交付审阅
- [ ] P1 50 个岗位全部有卡片；`evidence_level: full` 的比例写进报告
- [ ] P2 45 个岗位全部有卡片
- [ ] P3 能做多少做多少，写清未做的原因
- [ ] 每张卡片的每条陈述都能指到 evidence；核验脚本对全部卡片跑通，报告里给出删除条目数
- [ ] 计数类陈述可由脚本从样本复算
- [ ] 离线复现：不联网即可从 evidence 重新生成全部卡片和报告
- [ ] 报告结尾一节“对设计的影响”：哪些岗位的实际工作和提问树里的分支描述（/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/data/careerdb/question_tree_medical.json）不一致、需要调整分支；哪些岗位在招聘里名字相同但实际是两类工作，需要拆开
- [ ] 部分完成时按“部分验收”交付，写清完成到哪、缺什么

## 不做

- 不调研 A 支（医院/学术路线）岗位。
- 不修改小谷运行时代码、提示词、测试或 fixture；不改 build.py 的归类规则（发现归类错误写进报告，由 Claude 修）。
- 不使用招聘平台登录态，不用反检测浏览器，不注册账号、不发消息、不付费。
- 不给薪资结论（样本里出现的薪资可以记录在证据里，但卡片不写薪资范围）。
