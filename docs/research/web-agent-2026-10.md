# 小谷Web Agent形态、框架与模型调研（部分验收）

访问：2026-10-04/05，Asia/Shanghai。一手页面与文档记载，未注册竞品账号、安装框架、运行模型或部署。W1国内八工具已观察，但六个“AI实际界面”尚未全部证明；W2三方案文档比较，中文社区活跃度未知；W3官方价格与限制已核验，成本为公式估算。

## W1 国内工具形态

定位：面向中国大学生/应届生的岗位理解、简历与面试准备。直接竞品为效招、牛客AI、超级简历、智联求职AI、职徒52cv、知页；招聘平台BOSS/猎聘是相邻替代。源站未展示功能时记未知，不能用入口截图证明登录后工作台实际可用。

| 产品/官方来源 | 已观察形态与首屏动作 | 登录、免费额度与价格 | 信息来源展示 | 本次证据 |
|---|---|---|---|---|
| [效招Joblytic岗位看板](https://xzjobs.cn/products/job-board) | 公共看板演示岗位匹配、JD信号、问招招，工作台形态为演示 | 真实操作登录要求/额度/价格未找到 | JD与经历信号，员工引用未找到 | live-sources-2026-10/joblytic-job-board/cdp-page.json；此页截图缺 |
| [牛客AI面试](https://www.nowcoder.com/interview/ai/index) | 先选公司/岗位题库与面试入口；不是已执行聊天 | 页面有登录/注册；启动体验未测；免费额度/价格未找到 | 题库公司/年份，不证明答案逐项溯源 | live-sources-2026-10/nowcoder-ai，DOM+截图 |
| [BOSS直聘](https://www.zhipin.com/) | 招聘列表，先筛岗/登录；公开AI交互未找到 | 首页可看列表；AI配额和价格未知 | 招聘卡片，不等于AI答案 | live-sources-2026-10/boss-home（实际城市跳转） |
| [超级简历](https://www.wondercv.com/) | 简历模板/生成向导营销页；点击免费使用到登录链接 | 免费CTA不是无限额度；AI额度价格未找到；189元起是人类顾问 | 厂商称语料/表达模型与JD解析；没有逐项引用 | live-sources-2026-10/wondercv-home，DOM+截图 |
| [智联求职AI版](https://ai.zhaopin.com/) | 营销页聊天/简历/投递工作流演示，首步邀请体验 | 限量内测邀请文案；不证明实际可领取；当前额度价格未知 | 招聘数据库，未找到员工引用/日期 | live-sources-2026-10/zhaopin-ai，DOM+截图 |
| [猎聘](https://www.liepin.com/) | 招聘列表与简历优化入口；未核验AI求职工作台 | 职位详情公开可读、聊一聊要求登录；AI额度价格未知 | JD招聘方口径，不是员工反馈 | live-sources-2026-10/liepin-home，DOM+截图 |

厂商效果数字与演示不是实际转化或真实岗位覆盖。补充52cv及知页后，共6个有AI公开资料、2个招聘平台AI形态未验证，W1至少六AI产品的完整要求尚未满足；职徒以52cv官网核验；不采用自称官网的其他域名或多面鹅未确认域名。

推断：先让用户提交一句问题/JD/经历，服务端判断缺材料，再呈现结构化证据面板，比要求用户学习Skill名或参数更符合现有入口习惯。但是否提高完成率需产品实测，本轮没有用户行为数据。

## W2 三个开源实现方案

访问均10-05。仓库根与LICENSE页保存DOM+截图；Vercel LICENSE可见代码通过该页嵌入rawLines定向提取，保存source-lines.json，不采集用户会话信息。许可证是本次main分支快照，并非所有历史版本/依赖的统一许可；落地仍需锁版本核对。

| 方案/官方来源 | 许可证 | 对话+结构面板、工具trace | 服务端输出保证 | 部署复杂度（本次评估） | 中文社区活跃度 |
|---|---|---|---|---|---|
| [Chainlit](https://github.com/Chainlit/chainlit)、[LICENSE](https://github.com/Chainlit/chainlit/blob/main/LICENSE)、[Element](https://docs.chainlit.io/concepts/element)、[Step](https://docs.chainlit.io/concepts/step) | 当前Apache-2.0；不要沿用MIT旧印象 | Python Message/Step；side/page/inline元素、自定义JSX；ElementSidebar从Python设置；Step可仅显示工具调用 | Step是UI记录，不是强制路由；未找到它直接保证小谷Schema/逐字输出，需要自有校验及renderer | 原型较低：pip+Python入口；定制元素增前端依赖，生产鉴权/存储等另做，未部署验证 | 未做时间窗口/语言活跃统计，未知；星数不能代替中文社区 |
| [assistant-ui](https://github.com/assistant-ui/assistant-ui)、[LICENSE](https://github.com/assistant-ui/assistant-ui/blob/main/LICENSE) | MIT，Assistant Cloud可选托管另算 | React primitives、tool/JSON渲染、流式/重试/附件、人工确认；侧栏可由自有页面组合；不是仓库默认已具备小谷面板 | UI library不会替Python服务端执行路由和验证；需要后端契约 | 中等：React/TS与运行时adapter，可自有后端；Cloud不是必需，未实际接Python验证 | 未测；README全球社区不证明中文活跃 |
| [Vercel AI SDK](https://github.com/vercel/ai)、[LICENSE](https://github.com/vercel/ai/blob/main/LICENSE)、[结构输出](https://ai-sdk.dev/docs/ai-sdk-core/generating-structured-data)、[Generative UI](https://ai-sdk.dev/docs/ai-sdk-ui/generative-user-interfaces) | Apache-2.0 | useChat+工具结果React组件，可渲染input-available/output-available/output-error；侧边布局自行实现 | Output.object支持Zod/Valibot/JSON Schema并校验最终结果；流式partial对象未必可校验，必须等最终；Schema合法不证明事实正确 | 中等至高：TS服务端与React，复用Python需API桥接；不为选它重写业务；文档示例未实际运行 | 未测；全球star/commit数不构成中文指标 |

这是3个方案，满足3–5比较数量，但Vercel条目基于SDK和官方聊天实现文档，并未测试完整chat模板。未比较Open WebUI/LobeChat，不填无来源许可证。

反面证据：Chainlit仓库明确自2025-05-01社区维护，原团队退出维护；当前代码与发布存在不等于长期支持保证。Chainlit侧栏由Python直接设置的元素不持久化；若侧栏是决定的证据，必须由服务端保存结构化结果重建，不能靠UI状态。assistant-ui是UI层；Vercel SDK是TS工具层，二者都不自动实现小谷Pythonharness的事实边界。

**建议（暂定）**：保持Python服务端作为路由、工具、校验、渲染的唯一事实源；先在现有Web原型验证输出契约与证据面板。需要成熟聊天组件时优先以assistant-ui接自有API作候选；Chainlit适合快速内部原型，但社区维护与侧栏持久化需明确；不因框架宣传重写现有harness。未作部署选定或上线决定。

## W3 DeepSeek官方成本与限制

[价格表](https://api-docs.deepseek.com/quick_start/pricing/)10-05显示：

- 请求模型名deepseek-flash对应DeepSeek-V4.1-Flash；旧deepseek-v4-flash等别名仍接收，但旧模型已退役，由V4.1-Flash服务。
- deepseek-v4-pro对应DeepSeek-V4-Pro-0813。两者上下文1M、最大输出384K，JSON/工具调用支持。Flash支持视觉，Pro本页不支持。
- 默认thinking开启。官方价格可变，必须保留本次访问日期；没有人民币价格/汇率证据，不做人民币换算。

单位USD/百万token：

| 模型 | 时段 | 输入缓存命中 | 输入未命中 | 输出 | 账号并发 |
|---|---|---:|---:|---:|---:|
| Flash | 非高峰 | 0.003 | 0.15 | 0.60 | 2500 |
| Flash | 高峰 | 0.006 | 0.30 | 1.20 | 2500 |
| Pro | 非高峰 | 0.022 | 0.66 | 1.98 | 500 |
| Pro | 高峰 | 0.044 | 1.32 | 3.96 | 500 |

高峰UTC工作日01–04、06–10（中国法定节假日除外），对应北京时间09–12、14–18；其余含周末/中国假日为非高峰。没有推断访问当日是否官方假日。

按6000输入+1000输出，公式0.006×输入单价+0.001×输出单价：

| 模型 | 非高峰/全未命中 | 高峰/全未命中 | 非高峰/全命中 | 高峰/全命中 |
|---|---:|---:|---:|---:|
| Flash | $0.001500 | $0.003000 | $0.000618 | $0.001236 |
| Pro | $0.005940 | $0.011880 | $0.002112 | $0.004224 |

实际通常部分缓存命中，需按账单token分别计算；估算未包括额外thinking token、多轮上下文、失败重试、搜索API、工具耗时和部署费。不声称上述就是用户完整一轮账单。Pro单纯未命中单价估算约Flash的3.96倍，不能推出质量更优或成本更划算。

[并发/隔离文档](https://api-docs.deepseek.com/quick_start/rate_limit/)：2500/500是账号共享，多个key不增加额度，超过并发返回429；支持user_id隔离上下文/缓存/调度，但不增加账号总并发。拥塞请求可能有非流式空白keep-alive或SSE注释，超过约10分钟仍未开始推理关闭连接；客户端不能把keep-alive当结果。user_id设计使用内部非个人标识，不能直接放姓名/电话。

[JSON Mode](https://api-docs.deepseek.com/guides/json_mode/)：response_format为json_object，提示明确JSON及示例，max_tokens足够避免截断；官方记载有时返回空content。因此“开JSON模式=永远正确输出”不成立：需检测空内容、解析、Schema、事实范围、renderer逐字输出，失败有次数上限与明确状态。

[Thinking Mode](https://api-docs.deepseek.com/guides/thinking_mode/)：默认enabled/high，可enabled/disabled；minimal/low映射low，medium/high/xhigh映射high，max/ultra映射max。thinking时temperature/presence_penalty/frequency_penalty不生效；top_p小于0.95会被截到0.95，非thinking固定1。普通无工具下一轮不需回传reasoning_content；后续请求只要带tools参数，就须完整回传所有前轮reasoning_content，即使某轮没有实际调用工具；缺失可能400。它是服务端协议数据，不是给用户展示的产品trace。

## 对设计的影响

- 4.1保留服务端确定性route/missing_inputs/tool/validate/render；聊天框架只显示服务端确认后的结果，不能替代输出拦截。证据面板展示来源、日期、岗位范围和缺口；流式未校验数据必须明确暂态，不直接落为事实。
- trace记录路由、工具开始/结束、可引用证据和校验次数；不要展示模型内部推理内容或密钥。产品侧的人工确认来自明确动作与对象，竞品代聊演示不是小谷自动发送授权。
- 4.2模拟测试仍可用mock，真实模式需要账号key；默认Flash可作为成本基线的候选，先离线/小规模真实质量验收再决定Pro升级。不能仅凭价格表确定模型质量。
- 配置显式记录thinking模式、模型解析版本、价格访问日和重试上限，成本按真实usage统计；暂不改模型配置、运行时代码、部署或付费。

## 验收状态

W1部分：八工具观察、六有AI公开资料，实际AI互动与部分截图/额度仍未知，部分截图和价格未知。W2三方案官方比较已交付，许可证已定向核对；部署未实测、中文社区统计未做。W3官方价格、公式、JSON/thinking/并发限制已交付；没有API运行数据。设计影响为建议。

10-05公开静态补充：[52cv官网](https://www.52cv.com/)的简历/JD生成专属面试题、实时模拟与逐题反馈为厂商介绍，免费导出CTA不等于免费AI额度；[知页主页](https://www.zhiyeapp.com/)自述AI简历诊断。两者未实际启动体验，不能把静态页面当AI界面交互实测。52cv robots无法读取，未深入；相关方法证据在evidence/web-agent-2026-10/web-access-supplement.json。

证据目录evidence/web-agent-2026-10与复用live-sources-2026-10；每个语义目录有requested_url、实际url、accessed_at、text、links及截图。先前部分报告review不覆盖此稿，本轮独立只读审阅PASS（部分交付）。恢复见tasks/research-2026-10/start.md。

## 本轮收尾核验（2026-10-05）

独立只读审阅PASS（部分交付），Important修复已复核；见tasks/research-2026-10/review-2026-10-05.md。文件哈希清单为tasks/research-2026-10/evidence/manifest-final.json，不将错误/跳转页当正文。补效招截图的导航出现CDP_CONNECT_TIMEOUT，停止后续联网，未切路或重试；原证据保留。恢复见任务start.md，全部验收仍以正文缺口为准。

本轮静态补证已获独立只读审阅PASS（增量）；见tasks/research-2026-10/review-web-access-2026-10-05.md。完整验收缺口保持，原CDP超时不影响本轮静态已取得资料。
