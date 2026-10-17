# 执行与验收清单（准备完成，调研未完成）

顺序严格为 live-sources → web-agent → question-bank。网络失败后不启动后两份的联网采集。

## 第一份：岗位实时来源

| 项 | 实测/交付 | 当前 |
|---|---|---|
| Q1 | 国内≥5、海外≥2；来源/日期/招聘方与员工区分/降级逐格证据 | 待联网；只有2026-09-22效招本地旧报告 |
| Q2 | 牛客 robots、讨论与面经正文HTML、条款、作者标签与日期 | robots请求失败，未取正文 |
| Q3 | 四引擎两查询前十、返回数/详情率/日期；sitemap体量和更新 | 查询已预注册，未实测 |
| Q4 | 自建UA对候选站robots `*`；未知即未确认 | 未核验；脉脉按本次brief排除，无需再测 |
| Q5 | 五份真实JD、≤10条从业者分享；同字段真实JSON | 未采集；模拟样例保持原样 |
| Q6 | ≥4搜索API官方文档及五查询实测 | 查询已预注册，凭证/额度未核验 |

第一份完成后保存 docs/research/live-sources-2026-10.md，并在 upstream 1.3 回填证据支持的结论；上游第4节影响写报告。禁止把历史摘录当当日实测。

## 第二份：Web Agent

- W1：六个国内求职AI实际公开入口与首屏、登录、价格/额度、来源展示；厂商自述与真实操作分开。
- W2：Chainlit / Open WebUI / Vercel AI SDK / assistant-ui / LobeChat。许可证核对主仓库当前LICENSE和适用版本；JSON模式与服务端强制校验分开；trace UI和服务端审计分开；中文社区活跃度使用可复核统计窗口，不能靠星数证明。
- W3：DeepSeek官方当前模型名和价格优先核实；输入未缓存/缓存及输出分别列价。不确认型号存在前不沿用brief名称。成本公式：0.006×每百万输入价格 + 0.001×每百万输出价格（同币种）；thinking额外token另记，估算不等于账单。
- 输出 docs/research/web-agent-2026-10.md，并回填 upstream 1.2；未经上线授权不改部署或模型配置。

## 第三份：真实题库

- 严格保留原话，必要个人信息替换标记，不能把摘要当原话。
- CSV表头保持种子集14列；split留空，source只存原始URL。note存JSON：source_type、accessed_at、evidence_path、redactions、sampling_batch。freq_signal存原始数字与指标名，缺失填“未取到”。
- 来源类型 user/vendor/autocomplete 分开统计。点赞/浏览等是互动代理指标，不能换算真实提问人数或总体需求占比；搜索联想只能是该次可见信号，不能证明绝对频次。
- 先核验公开页面robots/条款；登录态尚未授权，不操作已登录会话。
- 按来源轮流采；每50条为一批，按记录顺序归类。初批已有类别不算“新类别”；新增定义固定后统计。两个连续批次各新增<2才可声明达到brief饱和；不足50不能冒充完整批次；各来源≤300、总量≤1500。
- coverage=N占比以user样本为分母另报来源偏差；不能把未采到的类别当“几乎不存在”。
- 新类别须定义、至少3条真实例句、条数；不能为凑例句改写或生成。
- 当前不生成real_questions.csv：零条真实数据的表头文件容易被误当交付，待采到正文后再写。
- 不切tune/holdout、不调用模型；第6节属于后续而非本次调研验收。

## 已发现的数据契约问题

1. tests/test_live_sources.py 的 MockFixtureTests.test_mock_posts_cannot_pass_as_real 强制当前mock样例所有帖子均为模拟。真实JSON单独放 examples/algorithm-engineer-real/live_sources.json；字段沿用原文件，mock=false、真实https URL、日期与标签来自正文。接入真实fixture测试属于必要的后续验收，不能以原mock测试通过冒充真实数据通过。
2. source_type不在种子集表头，暂以note JSON保存，不增加列；如以后改Schema需同步种子集和消费方。

## 恢复入口

读取本目录start.md与evidence/network-failure.json；用户同意正式权限复核后，保持原请求及代理在正式审批机制中复核。审批拒绝不绕过。网络恢复后先robots/条款，再访问允许路径；单站间隔≥3秒。证据化自检，当前未独立review；最终完整报告按工作区要求独立只读审阅。
