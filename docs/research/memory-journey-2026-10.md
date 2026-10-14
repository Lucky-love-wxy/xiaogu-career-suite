# 用户记忆与分批推进（求职旅程）调研

调研日期：2026-10-14（Asia/Shanghai）。范围：公开资料、官方文档和固定commit源码；无注册、登录、付费或招聘平台登录态；未修改小谷运行时、提示词、测试或隐私政策。

## 结论与完成边界

职业产品已提供持久简历、岗位/联系人、投递阶段和活动时间线；Teal Pro又明确以用户选择保存职业历史与决定。它们不能自动等同于“按用户对上一批方向的反馈生成下一批、再复盘”的完整旅程。通用助手的记忆可以由模型自动挑选，也提供查看、更正、删除；删除聊天与删除派生记忆并非同一动作。[FOREIGN-TEAL](https://www.tealhq.com/pro)；[FOREIGN-HUNTR](https://huntr.co/product/job-tracker)；[MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt)。

数量上找到了三条人生路径、3—5个职业选项的实践出处；未找到求职AI每批方向数量最优的实证。保存期限上，不能把网络日志不少于六个月直接当作全部聊天及画像留存六个月的依据。对应证据见C、D。

本报告完成全部问题的逐项调研与交付，但证据验收标为“部分验收”：LinkedIn因robots停止；BOSS 2025春招助手只获得官方ESG线索，未读报告正文；牛客目标正文为空；部分政策是2019/2021旧版。未知明确保留，不代表产品没有功能。Wiley摘要在补查robots前已取得，随后停止；该条只作有限摘要记录，C的两个完整方法依据为Stanford与FSU。未实测部署、中文准确率、产品登录界面或收费结账；原brief的Claude验收回填保持只读。

## A. 产品如何记住用户与推进

所有入口均来自公开说明/页面示意，不声称已登录验证。六问依次为：记什么；谁决定写；用户查看/修改/删除；推荐反馈下一批；复盘；免费/付费。每项的来源等级、日期、原文短摘及快照SHA在源索引中按证据编号查阅。

### BOSS直聘（含2025春招AI助手核验边界）

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 2019旧版官方政策列有简历、教育背景、城市及搜索浏览和聊天记录；不能据此证明2026 AI跨会话摘要或用户事实记忆。2025春招AI助手仅找到官方ESG线索，robots超时未继续正文核验。 | [DOM-BOSS-OLD](https://www.zhipin.com/web/common/protocol/protocol-2019-01-28.html)；[DOM-BOSS-2025-LEAD](https://ir.zhipin.com/system/files-encrypted/nasdaq_kms/assets/2026/04/29/9-28-11/2025%20Annual%20ESG%20Report%20%28CN%29.pdf) |
| 写入决定者 | 旧政策中用户完善简历，平台自动采集行为；AI决定记什么及逐条确认机制未能确认。 | [DOM-BOSS-OLD](https://www.zhipin.com/web/common/protocol/protocol-2019-01-28.html) |
| 用户控制及入口 | 公开首页提供隐私政策链接，但新版静态目标为空；2026查看/修改/删除记忆入口未能确认。 | [DOM-BOSS-HOME](https://www.zhipin.com/) |
| 反馈与下一批 | 旧政策说浏览搜索用于个性化推荐，公开首页有感兴趣/沟通过/已投递/面试状态；这些不证明AI按对话反馈调整下一批。未能确认批次循环。 | [DOM-BOSS-OLD](https://www.zhipin.com/web/common/protocol/protocol-2019-01-28.html)；[DOM-BOSS-HOME](https://www.zhipin.com/) |
| 阶段/结束复盘 | 未找到可核验的跨轮求职复盘说明；状态入口不等于复盘。 | [DOM-BOSS-HOME](https://www.zhipin.com/) |
| 免费/付费 | 未能确认2025春招AI助手或现行求职AI的免费/付费边界。 | [DOM-BOSS-2025-LEAD](https://ir.zhipin.com/system/files-encrypted/nasdaq_kms/assets/2026/04/29/9-28-11/2025%20Annual%20ESG%20Report%20%28CN%29.pdf) |

### 智联招聘 / 智联求职AI版

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 2025 V2政策明确结构化简历：专业/毕业时间/经历/期望城市等；AI预约页宣称追踪投递沟通事项。未能确认跨会话对话记忆。 | [DOM-ZH-PRIV](https://img01.zhaopin.com/2012/other/mobile/legal/protocol/2025/%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98%E9%9A%90%E7%A7%81%E6%94%BF%E7%AD%96_2025V2.pdf)；[DOM-ZH-AI](https://ai.zhaopin.com/) |
| 写入决定者 | 简历由用户填写，AI改写是自愿服务；求职AI关键回复先由用户确认。未能确认记忆写入是否逐条确认。 | [DOM-ZH-PRIV](https://img01.zhaopin.com/2012/other/mobile/legal/protocol/2025/%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98%E9%9A%90%E7%A7%81%E6%94%BF%E7%AD%96_2025V2.pdf)；[DOM-ZH-AI](https://ai.zhaopin.com/) |
| 用户控制及入口 | 政策说明App“我的”编辑简历，网页“我的简历”等查看；App“我的→附件简历已上传”删除附件，其他信息可请求删除。AI记忆专门入口未能确认；未实测登录界面。 | [DOM-ZH-CONTROL](https://img01.zhaopin.com/2012/other/mobile/legal/protocol/2025/%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98%E9%9A%90%E7%A7%81%E6%94%BF%E7%AD%96_2025V2.pdf) |
| 反馈与下一批 | 官网宣称按匹配优先级投递、代聊、追踪、关键回复确认；未明确用户打分或随口反馈如何改变下一批。营销说明不能代替实际闭环验证。 | [DOM-ZH-AI](https://ai.zhaopin.com/) |
| 阶段/结束复盘 | 网页有“求职统计”（政策载明），求职AI有进度追踪；未找到阶段/结束复盘功能。 | [DOM-ZH-CONTROL](https://img01.zhaopin.com/2012/other/mobile/legal/protocol/2025/%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98%E9%9A%90%E7%A7%81%E6%94%BF%E7%AD%96_2025V2.pdf)；[DOM-ZH-AI](https://ai.zhaopin.com/) |
| 免费/付费 | 公开页仍提供内测预约及登录体验，未列AI收费或免费额度，未能确认。 | [DOM-ZH-AI](https://ai.zhaopin.com/) |

### 牛客

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 公开首页确认简历助手、一键网申及AI模拟面试入口；目标介绍页仅4行空壳，实际持久字段/跨会话记忆未能确认。 | [DOM-NC-HOME](https://www.nowcoder.com/home/)；[DOM-NC-EMPTY](https://www.nowcoder.com/my/resume-plugin-intro) |
| 写入决定者 | 未能确认用户手填/模型提取/确认后写入机制；入口不足以证明实现。 | [DOM-NC-HOME](https://www.nowcoder.com/home/)；[DOM-NC-EMPTY](https://www.nowcoder.com/my/resume-plugin-intro) |
| 用户控制及入口 | 未能确认查看/改/删记忆入口；未登录。 | [DOM-NC-EMPTY](https://www.nowcoder.com/my/resume-plugin-intro) |
| 反馈与下一批 | 未能确认按用户反馈调整下一批推荐。 | [DOM-NC-EMPTY](https://www.nowcoder.com/my/resume-plugin-intro) |
| 阶段/结束复盘 | 未找到可核验的个人旅程复盘功能；社区面经与平台为个人复盘是不同事实。 | [DOM-NC-HOME](https://www.nowcoder.com/home/)；[DOM-NC-EMPTY](https://www.nowcoder.com/my/resume-plugin-intro) |
| 免费/付费 | 未能确认AI求职/记忆功能收费边界；搜索发现NowClaw免费使用说法，但未继续核验正文，不采为结论。 | [DOM-NC-EMPTY](https://www.nowcoder.com/my/resume-plugin-intro) |

### 超级简历 WonderCV

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 2021政策列有账户、工作经历/技能、浏览点击操作记录及与招聘者聊天记录，保存简历用于投递。聊天留存不等于AI跨会话摘要；未能确认AI记忆。 | [DOM-WCV-PRIV](https://www.wondercv.com/newPrivacy) |
| 写入决定者 | 用户填写上传简历；平台自动收集日志并提取偏好标签。未能确认AI记忆写入或用户逐条确认。 | [DOM-WCV-PRIV](https://www.wondercv.com/newPrivacy) |
| 用户控制及入口 | 政策载明网页“我的超级简历→个人账户”，App“我的超级简历→设置”查询更正删除个人资料；注销需客服。专门AI记忆入口未能确认，界面未实测。 | [DOM-WCV-CONTROL](https://www.wondercv.com/newPrivacy) |
| 反馈与下一批 | 政策说明依据日志提取偏好画像用于推送；未能确认投递/对话反馈改变下一批方向的循环。 | [DOM-WCV-PRIV](https://www.wondercv.com/newPrivacy) |
| 阶段/结束复盘 | 未找到阶段性/结束求职复盘说明。 | [DOM-WCV-PRIV](https://www.wondercv.com/newPrivacy) |
| 免费/付费 | 公开页同时有免费模板分类和开通超级会员入口；具体AI额度、价格及免费/付费记忆边界未能确认。 | [DOM-WCV-PRICE](https://www.wondercv.com/jianlimoban/xianshiyouhui/) |

### Kimi Memory（通用助手对照）

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 官方帮助确认跨会话记偏好/习惯/风格、身份及关心事项；最多50条，每条500字符。公开帮助没有披露底层存储schema，不认定为简历字段库。 | [DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space) |
| 写入决定者 | 专门训练的模型选择有价值会话内容，自然对话触发；用户可明确说记住；帮助未说每条自动记忆均先确认。 | [DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space) |
| 用户控制及入口 | 网页/App个人主页→设置→记忆指令查看删除；对话可更正替换、删单条或全部、询问已记内容；可关闭清空。 | [DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space) |
| 反馈与下一批 | 对话纠正能替换旧记忆并影响后续回答；未找到专门“求职推荐→反馈→下一批”的成套流程。 | [DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space) |
| 阶段/结束复盘 | 可问当前记住什么，这是记忆查看；未找到阶段/结束求职复盘机制。 | [DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space) |
| 免费/付费 | 记忆帮助及会员页未明确此功能的免费/付费边界，未能确认。 | [DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space)；[DOM-KIMI-PRICE](https://www.kimi.com/help/membership) |

### LinkedIn AI 求职功能

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 未能确认。本次读取 robots 后停止 LinkedIn 自动访问，未登录、未注册；不把搜索摘要当成功能正文证据。 | [FOREIGN-LI-STOP](https://www.linkedin.com/robots.txt) |
| 写入决定者 | 未能确认。本次读取 robots 后停止 LinkedIn 自动访问，未登录、未注册；不把搜索摘要当成功能正文证据。 | [FOREIGN-LI-STOP](https://www.linkedin.com/robots.txt) |
| 用户控制及入口 | 未能确认。本次读取 robots 后停止 LinkedIn 自动访问，未登录、未注册；不把搜索摘要当成功能正文证据。 | [FOREIGN-LI-STOP](https://www.linkedin.com/robots.txt) |
| 反馈与下一批 | 未能确认。本次读取 robots 后停止 LinkedIn 自动访问，未登录、未注册；不把搜索摘要当成功能正文证据。 | [FOREIGN-LI-STOP](https://www.linkedin.com/robots.txt) |
| 阶段/结束复盘 | 未能确认。本次读取 robots 后停止 LinkedIn 自动访问，未登录、未注册；不把搜索摘要当成功能正文证据。 | [FOREIGN-LI-STOP](https://www.linkedin.com/robots.txt) |
| 免费/付费 | 未能确认。本次读取 robots 后停止 LinkedIn 自动访问，未登录、未注册；不把搜索摘要当成功能正文证据。 | [FOREIGN-LI-STOP](https://www.linkedin.com/robots.txt) |

### Teal（Teal Pro 与 Teal+ 分开）

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | Teal Pro 官方公开页记载保存经历、项目、成果、技能、目标、感兴趣职位、联系人及已作决定；公开 Career Profile/Career Vault 示意可见。未公开底层是否结构化表或对话摘要。 | [FOREIGN-TEAL](https://www.tealhq.com/pro) |
| 写入决定者 | Teal Pro 写明由用户选择保存；可手记成果。Google 联系人/Calendar 接入默认关闭，用户开启后导入并维护网络；不能据此推断每轮自动抽取聊天。 | [FOREIGN-TEAL](https://www.tealhq.com/pro) |
| 用户控制及入口 | 官网明确可查看、纠正、移除数据；公开示意有 Career Profile、People、Opportunities、Chat 和 Add/Save。逐条修改删除的实际入口未能确认。Google 撤权入口为 Google Account。 | [FOREIGN-TEAL](https://www.tealhq.com/pro) |
| 反馈与下一批 | Opportunity Fit 以经历和目标对照岗位，联系人/日历支撑跟进提醒。未找到按用户对上一批方向的反馈自动调整下一批的公开说明。 | [FOREIGN-TEAL](https://www.tealhq.com/pro) |
| 阶段/结束复盘 | 提及准备职业review、面试及每日 Career Digest；未能确认求职阶段或结束时自动复盘。不能把 Daily Digest 当求职过程复盘。 | [FOREIGN-TEAL](https://www.tealhq.com/pro) |
| 免费/付费 | Teal+定价页：核心简历和无限Job Tracking免费；Teal+ $13/7天、$29/30天、$79/90天，增加AI/分析功能。Teal Pro职业记忆页面未给价格，不能把Teal+价格套给Teal Pro。 | [FOREIGN-TEAL-PRICE](https://www.tealhq.com/pricing)；[FOREIGN-TEAL](https://www.tealhq.com/pro) |

### Careerflow

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 官方公开页确认简历、投递进展、Networking Tracker、Document Storage；属于可持续账户资料/跟踪信息。未找到跨会话对话记忆说明。 | [FOREIGN-CF](https://www.careerflow.ai/) |
| 写入决定者 | 有AI简历生成、Application Autofill和Automated Job Tracking，但公开首页不足以确定哪些用户事实自动保存、是否逐条确认；未能确认记忆写入策略。 | [FOREIGN-CF](https://www.careerflow.ai/) |
| 用户控制及入口 | 公开页有Job Tracker入口和产品示意，确认可监测进展；逐项修改/删除入口未能确认，不由营销图推断。 | [FOREIGN-CF](https://www.careerflow.ai/) |
| 反馈与下一批 | 可监测投递进展、分析Job Fit、按JD定制材料；未找到反馈上一批推荐后自动调整下一批的官方说明。 | [FOREIGN-CF](https://www.careerflow.ai/) |
| 阶段/结束复盘 | Premium Plus列Interview Analysis；这是面试分析，未能确认覆盖完整求职旅程的阶段/终局复盘。 | [FOREIGN-CF](https://www.careerflow.ai/) |
| 免费/付费 | Basic免费且Tracker/Networking/存储有限。首页多个计费周期并列：Premium $8.99/周或$23.99/月，Premium Plus $19.99/周或$44.99/月；未结账，促销和年/季付条件以实际公开页为准。 | [FOREIGN-CF](https://www.careerflow.ai/) |

### Huntr

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 保存职位描述、薪酬、联系人、材料和活动时间线；每职位可关联独立简历/求职信，并记录面试时间。未找到对话摘要记忆说明。 | [FOREIGN-HUNTR](https://huntr.co/product/job-tracker) |
| 写入决定者 | 用户用Chrome Job Clipper一键保存职位、上传材料、记录面试、拖拽看板变更阶段。未能确认模型自动抽取并持久保存聊天事实。 | [FOREIGN-HUNTR](https://huntr.co/product/job-tracker) |
| 用户控制及入口 | 公开文档确认Kanban板可拖拽阶段、查看活动时间线、管理材料和联系人；逐条删除/数据记忆管理入口未能确认。 | [FOREIGN-HUNTR](https://huntr.co/product/job-tracker) |
| 反馈与下一批 | 用户手动更新投递/面试阶段，Metrics用于了解进展和改进策略；未能确认平台据结果自动生成下一批方向。 | [FOREIGN-HUNTR](https://huntr.co/product/job-tracker) |
| 阶段/结束复盘 | 有完整投递到offer活动时间线和Job Search Metrics，支持用户回看；未找到自动阶段性/结束时叙事复盘。 | [FOREIGN-HUNTR](https://huntr.co/product/job-tracker) |
| 免费/付费 | Free最多100职位、基本洞察；Pro无限跟踪/高级指标，$40/月，$90/3个月或$160/6个月。产品页写$30/月而定价页写$40月付：保留不一致，$30对应季付折算，不替官网裁决。 | [FOREIGN-HUNTR](https://huntr.co/product/job-tracker)；[FOREIGN-HUNTR-PRICE](https://huntr.co/pricing) |

### Claude Memory（新旧体验区分）

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 新版以独立Topics保存角色/项目、人和地点、沟通/工作偏好、技术偏好、持续工作；项目有独立memory和summary。旧版24小时对话综合摘要仅legacy。 | [FOREIGN-CLAUDE](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| 写入决定者 | 新版随聊天自动保存，也可要求remember this；并非每条先确认。敏感topics默认不存，用户另开启；部分身份/账户信息即使要求也不存。 | [FOREIGN-CLAUDE](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| 用户控制及入口 | Settings > Memory > Topics选择主题，edit图标修改或Delete删除；也能在聊天中要求记住/修改/忘记。Pause与Reset区分，删除对话不自动删除新版相关topics。 | [FOREIGN-CLAUDE](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| 反馈与下一批 | 用户在聊天更正记忆会影响下一对话；付费past-chat-search用RAG引用原聊天。但未找到专门求职『推荐—反馈—下一批』产品流程说明。 | [FOREIGN-CLAUDE](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| 阶段/结束复盘 | 项目有summary；官方旧版段落指向monthly recap，新版是否同样提供尚未确认，不能混写。未确认求职终局复盘。 | [FOREIGN-CLAUDE](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |
| 免费/付费 | 新版Memory在Free/Pro/Max默认开启；past chat search为付费Pro/Max/Team/Enterprise。Team/Enterprise由组织能力及成员设置控制。 | [FOREIGN-CLAUDE](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) |

### ChatGPT Memory（通用对照）

| 问题 | 公开证据支持的答案与边界 | 证据 |
|---|---|---|
| 记住什么 | 跨聊天使用偏好和相关信息，来源可含聊天、独立saved memories、文件/连接应用；记忆摘要并不展示全部内容。 | [MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt) |
| 写入决定者 | 用户可要求记住；系统也可挑选有用信息自动保存或更新，不要求每条先确认。 | [MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt) |
| 用户控制及入口 | Settings → Personalization → Memory；可纠正/删除，入口依套餐而变。删聊天不等于删记忆；彻底移除还须删除相应来源。 | [MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt) |
| 反馈与下一批 | 可在对话中纠错并改变以后个性化；未能确认求职推荐分批循环。 | [MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt) |
| 阶段/结束复盘 | Memory summary是相关上下文摘要；未能确认求职阶段/结束复盘。 | [MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt) |
| 免费/付费 | 免费套餐有有限记忆，付费扩展；具体入口依地区、套餐、平台。未验证账户。 | [MAIN-A09P](https://openai.com/chatgpt/pricing/)；[MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt) |

## B. 开源长期记忆方案

同名项目的新旧版本可能有不同运行架构。下面按本次固定commit说明，不把README的效果自述当独立效果验证，也不把底层能接本地模型等同于已验证中文效果。

### mem0 OSS Python SDK

版本/commit：`d26ba5e4518cef7fff3c66d4f715b21adf9feabe`。

| 项目 | 结论与边界 | 证据 |
|---|---|---|
| 记忆分类/存储 | 以 user_id/agent_id/run_id 隔离用户、agent、会话事实；主要是事实文本+向量+metadata（含角色、来源、时间、关联记忆），SQLite 保存历史及最近消息。源码单独处理 procedural_memory；不是强制把事实/事件/反思分成四个数据库，也没有求职旅程 schema。 | [oss-mem0-source-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/main.py)；[oss-mem0-source-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/configs/base.py) |
| 选择写入/更新/冲突 | 调用方决定何时调用 add；infer=True 默认由 LLM 选择值得记录的内容，infer=False 直接写非 system 消息。当前 V3 执行路径采用 ADD-only，查相近旧记忆、单次抽取、hash 去重、关联旧记忆；矛盾记录新增并链接而非自动覆写旧值。另有显式 update/delete 和 expiration_date。源码 add 的 docstring 仍描述自动增改删，与当前执行路径及 README 不一致，不能当现行默认。用户确认、纠错审批仍须应用另做。 | [oss-mem0-source-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/main.py)；[oss-mem0-extra-3](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/configs/prompts.py)；[oss-mem0-readme](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/README.md) |
| 读取与token | search 相关检索，可设 top_k；当前默认 top_k=20；语义、BM25 与实体信号依赖后端及可选 NLP。调用方选择哪些结果进入 prompt，不要求每轮全量。token 减少是检索子集的机制推断；写入仍耗 LLM/embedding，不能把 README 托管平台 benchmark 当 OSS 本地效果或中文 token 承诺。 | [oss-mem0-source-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/main.py)；[oss-mem0-extra-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/vector_stores/qdrant.py)；[oss-mem0-readme](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/README.md) |
| 部署及境外依赖 | 不能理解为仅 Python+SQLite：SQLite 是 history.db；默认 vector provider=qdrant，无远端参数时走 QdrantClient(path=...)，支持本地嵌入式向量存储而不必另起向量服务。默认 LLM/embedding 访问 OpenAI；官方 Ollama 配置可换本地模型，但还需要 Ollama 推理进程、模型文件和向量依赖。库、Docker 自托管服务、云平台是三种交付形态，不等价。遥测有外发路径，完全本地须另核验并关闭。 | [oss-mem0-source-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/configs/base.py)；[oss-mem0-extra-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/vector_stores/configs.py)；[oss-mem0-extra-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/vector_stores/qdrant.py)；[oss-mem0-source-4](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/docs/cookbooks/companions/local-companion-ollama.mdx)；[oss-mem0-readme](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/README.md)；[oss-mem0-extra-4](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/telemetry.py) |
| 许可与中文证据 | Apache-2.0。未找到独立中文记忆准确率评测。实际中文/多语言问题有公开反馈：issue #4884（三级用户报告）称 BM25/实体信号退化，PR #6718 提出中文 pipeline 修复但取证时 open、merged=false；不能视作已发布修复。当前抽取 prompt 支持 use_input_language，但函数默认 False，执行调用未打开该选项；中文保持同语不能仅凭旧 prompt 推定。 | [oss-mem0-source-3](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/LICENSE)；[oss-mem0-issue-4884](https://api.github.com/repos/mem0ai/mem0/issues/4884)；[oss-mem0-pr-6718](https://api.github.com/repos/mem0ai/mem0/pulls/6718)；[oss-mem0-extra-3](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/configs/prompts.py)；[oss-mem0-source-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/main.py) |
| 失败案例/已知问题 | 具体已知问题：#4884 报告非英文 BM25 无命中/实体 boost 丢失；当前代码固定英文 spaCy 可核验。源码对抽取 JSON 解析失败返回空记忆列表（与无事实相同表象），LLM 请求异常则抛 LLMError；Qdrant 旧 collection 无 BM25 sparse slot 时降为语义搜索并警告。ADD-only 会留下历史矛盾，需要检索/上层来源及时间策略判别；这是源码机制风险，不是已测出的错误率。未找到可直接适用于当前 commit 的“不该记的隐私内容”事故统计。 | [oss-mem0-issue-4884](https://api.github.com/repos/mem0ai/mem0/issues/4884)；[oss-mem0-verify-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/utils/spacy_models.py)；[oss-mem0-verify-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/utils/lemmatization.py)；[oss-mem0-source-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/main.py)；[oss-mem0-extra-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/vector_stores/qdrant.py) |

### Letta 当前活跃源（Letta Code；原 MemGPT）

版本/commit：`c76fd84a61d64cfd3d9a9730205f67bd4230c818`。

| 项目 | 结论与边界 | 证据 |
|---|---|---|
| 记忆分类/存储 | 原 letta 仓库当前 main 明确 V1 Python API server 已 retired，历史源在 archive；现行活跃源为 letta-code。当前 MemFS：根 MEMORY.md 索引、根 Markdown core memory（常驻）、子目录 deferred memory（按需读）、skills（程序性记忆），Git 跟踪；本地对话/compaction 以 JSONL/JSON 存。不能把旧 core/recall/archival 文档冒充当前部署的默认。 | [oss-letta-readme](https://raw.githubusercontent.com/letta-ai/letta/5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a/README.md)；[oss-letta-extra-4](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/subagents/builtin/reflection-v2.md)；[oss-letta-extra-3](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/local-store.ts)；[oss-letta-extra-6](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/system-prompt-compilation.ts) |
| 选择写入/更新/冲突 | 主 agent 可改 memory；可配置周期 dreaming/reflection，由后台 agent 看近期或多会话 transcript，筛掉临时、已记录信息，针对纠错/偏好/事实更新文件。反思 prompt 要求以最新证据替换陈旧事实，不并列保留矛盾；用户要求忘记、敏感或错误内容应删除。语义冲突依靠 agent 判断，不是确定性冲突规则；Git 合并冲突另有 repair worker、锁与 attempted 状态。不是每轮强制反思，需配置触发策略。 | [oss-lettacode-verify-1](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/README.md)；[oss-letta-extra-4](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/subagents/builtin/reflection-v2.md)；[oss-letta-extra-5](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/memory-conflict-repair.ts) |
| 读取与token | core 内容和索引/描述常驻 prompt，deferred/skill 正文按需读取；支持消息搜索。本地 transcript-search 明确不支持 vector/hybrid，只支持 fts（源码含 CJK substring 处理）。token 随 core 大小和选读变化；后台反思另耗模型调用。该机制不能推出固定节省比例。 | [oss-letta-extra-4](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/subagents/builtin/reflection-v2.md)；[oss-letta-extra-6](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/system-prompt-compilation.ts)；[oss-letta-extra-7](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/transcript-search.ts) |
| 部署及境外依赖 | 当前活跃实现是 npm/Node 而非 Python 库；本地 MemFS Git + 磁盘 JSON/JSONL，无须向量服务的本地消息检索已经存在。因此不能直接在“仅 Python+SQLite”约束下即插即用。README 默认 Letta Cloud，提供 backend local；本地状态不代表本地推理，LLM provider 仍另配置。可自托管 App Server；未运行或验证其完全离线部署。历史 Python server 可复现但已退休，不建议把它算作现行支持。 | [oss-letta-readme](https://raw.githubusercontent.com/letta-ai/letta/5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a/README.md)；[oss-lettacode-verify-1](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/README.md)；[oss-lettacode-verify-2](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/package.json)；[oss-letta-extra-3](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/local-store.ts)；[oss-letta-extra-7](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/transcript-search.ts) |
| 许可与中文证据 | Apache-2.0。未找到独立中文长期记忆效果评测；找到中文使用界面反馈 #2644：IME 候选窗错位（2026-06-01 举报，2026-07-03 closed），这是界面问题，不能推定当前中文记忆准确率低或故障仍在。当前检索源码有 CJK 子串匹配，说明适配机制，不等于效果评测。 | [oss-letta-extra-1](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/LICENSE)；[oss-letta-issue-2644](https://api.github.com/repos/letta-ai/letta-code/issues/2644)；[oss-letta-extra-7](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/transcript-search.ts) |
| 失败案例/已知问题 | 具体边界：本地 vector/hybrid 搜索抛不支持错误；MemFS 未提交/无可读 revision 会导致编译为空 core；不可读已提交文件被 best-effort 跳过。Git 冲突修复存在已尝试但无法解决状态；反思依赖模型选择与改写，未找到当前 commit 的语义错记率公开评测。README 明确原生 Windows 自动 dreaming 默认关闭，手动可用，这是平台限制不是记忆全失效。 | [oss-letta-extra-7](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/transcript-search.ts)；[oss-letta-extra-6](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/system-prompt-compilation.ts)；[oss-letta-extra-5](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/memory-conflict-repair.ts)；[oss-lettacode-verify-1](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/README.md) |

### LangGraph 长期记忆 Store（Python）

版本/commit：`a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5`。

| 项目 | 结论与边界 | 证据 |
|---|---|---|
| 记忆分类/存储 | Store 是按 namespace tuple + key 存 JSON mapping 的通用跨会话数据层，Item 有 created_at/updated_at。用户事实、事件、批次反馈、复盘都可由应用定义 value schema；Store 本身不抽取、不规定四种记忆。InMemoryStore 是进程内字典，退出丢失。当前仓库已有官方 SqliteStore，和线程 checkpointer 是不同类。 | [oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py)；[oss-langgraph-source-2](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/memory/__init__.py)；[oss-langgraph-source-4](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py) |
| 选择写入/更新/冲突 | 应用/图节点决定何时 put、get、delete。同 namespace+key 的 put 更新/替换值；SqliteStore 批次同键去重后 INSERT OR REPLACE，并支持 TTL/sweep。是否记忆、模型还是用户确认、版本冲突/事实矛盾的语义合并由应用实现。TTL 是技术过期机制，不能替代同意、最小化和删除流程。 | [oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py)；[oss-langgraph-source-4](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py) |
| 读取与token | get 精确读；search 有 namespace、metadata filter、limit/offset，配置 index 后才有语义检索；InMemory 默认不启用 embedding。Store 不自动把结果塞进 prompt，图节点自行装配。token 由抽取节点、embedding、召回数量、注入字段决定；未找到可通用于任意 Store 图的节省比例。 | [oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py)；[oss-langgraph-source-2](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/memory/__init__.py)；[oss-langgraph-source-4](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py) |
| 部署及境外依赖 | 可以用 Python + SQLite 文件在单机跑当前官方 SqliteStore；有 sqlite_vec/orjson 等库依赖，无须额外向量数据库服务。不启用 index 时普通字段存取不需境外调用；语义检索可传自定义本地 embedding。官方示例出现 OpenAI embedding 只是示例，不是库强制默认。SqliteStore 同步类不支持 async，应另用 AsyncSqliteStore；本次只源码确认，不做安装/并发/耐久测试。 | [oss-langgraph-source-4](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py)；[oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py)；[oss-langgraph-verify-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/pyproject.toml) |
| 许可与中文证据 | MIT（仓库主许可；各组件另核验）。未找到独立中文长期记忆效果评测；Store 的中文保存/语义效果取决于应用 schema、embedding 和 LLM。找到 #8514 中文 Windows GBK 环境 langgraph dev 启动失败的用户报告，但属 API/CLI 读取编码，不是 SQLite Store 中文检索评测或 Linux 服务器必然失败。 | [oss-langgraph-source-5](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/LICENSE)；[oss-langgraph-issue-8514](https://api.github.com/repos/langchain-ai/langgraph/issues/8514) |
| 失败案例/已知问题 | 可核验失败边界：InMemoryStore 进程退出数据丢失；无 index 时语义搜索不启用；SqliteStore 同步类 async 调用不支持。已公开 #8514 报告 CLI/API locale 编码失败，不能外推为核心 Store 缺陷。Store 不自动验证事实/敏感信息，若应用盲 put 则原样持久化；这是职责边界推断，不是 LangGraph 已确认隐私事件。 | [oss-langgraph-source-2](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/memory/__init__.py)；[oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py)；[oss-langgraph-source-4](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py)；[oss-langgraph-issue-8514](https://api.github.com/repos/langchain-ai/langgraph/issues/8514) |

### Graphiti OSS（与 Zep 托管服务区分）

版本/commit：`8d8a12a22452cbef9335792afb73b8cbfe6a79fa`。

| 项目 | 结论与边界 | 证据 |
|---|---|---|
| 记忆分类/存储 | 记忆组成：entity 节点及摘要、fact/relationship 边、episode 原始事件及来源、开发者 ontology；边有有效时间范围，可追溯来源 episode。Graphiti 默认 store_raw_episode_content=True；不是自动提供求职用户表/线程管理的完整助手服务。Zep 是托管 context infrastructure，不能把其 user/thread、治理、性能承诺算作 OSS 功能。 | [oss-graphiti-readme](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/README.md)；[oss-graphiti-source-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/graphiti.py) |
| 选择写入/更新/冲突 | 调用方决定哪些 episode 入库；add_episode 做 LLM 实体/关系抽取、去重、embedding、边冲突解决。LLM 提示词区分 duplicate 与 contradicted facts；新信息使旧边失效，历史保留，不直接删掉旧事实。不是每轮自动运行，选择有价值/征求用户确认要应用决定；时间失效不等于用户删除个人信息。 | [oss-graphiti-source-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/graphiti.py)；[oss-graphiti-extra-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/prompts/dedupe_edges.py) |
| 读取与token | search 是语义+关键词+图关系的混合召回，返回相关关系，可用 recipes/重排；调用方装配到 prompt。检索减少需注入的候选历史是机制推断，写入的实体抽取/去重/摘要和重排可能另耗模型 token；未找到对当前 OSS 中文求职场景通用 token 成本实证。 | [oss-graphiti-source-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/graphiti.py)；[oss-graphiti-readme](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/README.md) |
| 部署及境外依赖 | 不能仅 Python+SQLite：默认 Neo4j；可选 FalkorDB、Neptune 等图后端，FalkorDB Lite 可嵌入但不是 SQLite；Kuzu 当前 deprecated。默认 OpenAI LLM/embedder/reranker；官方支持 OpenAI-compatible 本地 Ollama/vLLM 等，能避免默认境外推理调用但需图存储+本地模型服务。README 遥测 opt-out，完全本地还需关闭 GRAPHITI_TELEMETRY_ENABLED。Zep 托管与 Graphiti 本地自建的境外依赖需分开评估。 | [oss-graphiti-readme](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/README.md)；[oss-graphiti-source-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/graphiti.py)；[oss-graphiti-source-2](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/llm_client/config.py) |
| 许可与中文证据 | Apache-2.0。未找到独立中文长期记忆基准；找到三级用户反馈 #312（2025-03-31）：中文自建库效果不错，但总结/推断仍混英文。评论表示计划跟随 episode 语言，后续追问进展；issue closed 本身不能证明已修复。该反馈距本次逾一年，仅作历史故障线索，不能评定当前中文水平。 | [oss-graphiti-source-3](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/LICENSE)；[oss-graphiti-issue-312](https://api.github.com/repos/getzep/graphiti/issues/312)；[oss-graphiti-comments-312](https://api.github.com/repos/getzep/graphiti/issues/312/comments) |
| 失败案例/已知问题 | 官方 README 明确小/本地模型可能生成不合 schema 的 JSON 导致抽取失败；支持 json_schema/json_object 切换但无准确性保证。官方提醒 LLM provider 429 风险、需低并发；Kuzu 上游未维护而弃用。#312 是中英混杂历史反馈。LLM 判断关系矛盾/重复不是事实真值保证；未找到当前 OSS 的敏感信息误记事故统计。 | [oss-graphiti-readme](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/README.md)；[oss-graphiti-extra-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/prompts/dedupe_edges.py)；[oss-graphiti-issue-312](https://api.github.com/repos/getzep/graphiti/issues/312) |

### Generative Agents的反思

2023 arXiv v1 §4.1—4.3：观察以自然语言存入memory stream；按相关性、近期性、重要性检索。新事件重要性累计达到阈值时生成高层问题，检索证据，再生成带原记忆指针的反思；反思也会成为后续检索对象。§6.5.2/7.2同时记录漏检和虚构补充。对小谷的启发是复盘结论应指回具体反馈事件、与用户事实分开并可被纠正；这是迁移推断。其25个模拟人物的可信度评估不是求职改善或中文记忆评测，不能直接采纳模拟阈值/频率。 [MAIN-B05](https://arxiv.org/html/2304.03442v1)

## C. 分批探索与反馈循环依据

### Stanford Life Design：原型对话与原型体验

事实：2024官方Studio课件要求访谈正在过你感兴趣未来的人，听其经历；体验原型先得到切身感受再投入更多资源。原型应便宜、快、可接近，用于暴露假设、降低风险和学习。课件让参与者提出需要更多信息的部分，再选择能带来学习的动作。推断：可将『方向→具体未知→JD/从业者/低成本体验→实际反馈→修正方向』用作小谷批次推进依据；JD阅读是本研究迁移，不是课件原句。它不是证明AI分三批推荐有效的实证。 [FOREIGN-STANFORD](https://lifedesignlab.stanford.edu/s/June-Virtual-2024-Studio-Day-2-compressed.pdf)

### Planned Happenstance（计划性偶发/机缘学习）

事实：Mitchell、Levin、Krumboltz，Journal of Counseling & Development 77:115–124（1999）公开摘要要求开展探索活动，提高遇到意外职业机会的概率，把未计划事件变成学习机会。推断：回访应收集新接触、新机会和意外发现，下一批允许改向，不只对第一批打分。限制：仅官方公开摘要已读取；全文未读，Wiley robots补查含GPTBot拒绝后停止进一步访问；不能声称检验了完整咨询干预或因果效果。 [FOREIGN-PLANNED](https://onlinelibrary.wiley.com/doi/10.1002/j.1556-6676.1999.tb02431.x)

### 推荐系统探索/利用：contextual bandit

事实：Li/Chu/Langford/Schapire WWW 2010论文以用户和候选项的上下文选项，并按实际点击反馈更新策略。仅能看到选中/展示行动的反馈；表面最佳可能因知识不足而并非最佳，需保留探索。新闻实验不是求职实验。迁移推断：少反馈阶段同时保留已显示契合的方向和少量不同假设的方向，记录展示与反馈上下文；『没投』可能是没时间/地域/信息不足，不能直接当不喜欢，『没回音』不能直接当不适合。无足够重复数据时先用可解释规则，无证据支持直接训练bandit就更好。 [FOREIGN-BANDIT](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/p661.pdf)

### 每批几个方向

找到两种可靠教学/咨询经验：Stanford 2024 Studio练习三条明显不同的五年人生路径；FSU CASVE官方指南建议收窄到3—5个职业/专业/工作选项。两者均不是证明AI每批方向数量最优的实验。未找到本轮求职推荐每批2/3/5个最优的实证；不可把少量选项经验写成统一上限，也不能说数量依据完全不存在。数量仍须结合用户信息量与实际行动反馈验证。 [FOREIGN-STANFORD](https://lifedesignlab.stanford.edu/s/June-Virtual-2024-Studio-Day-2-compressed.pdf)；[MAIN-CFSU](https://career.fsu.edu/students/career/planning/decision-making/guide-to-good-decision-making)；[FOREIGN-NUMBER-SEARCH](https://link.springer.com/article/10.1007/s10775-024-09720-4)

### CASVE：扩展/收窄—试做—返回检查

FSU官方指南将自我与职业知识学习、扩展收窄、价值排序、执行、回看组成循环；执行包括兼职/志愿体验或课程培训试验选择，回看检查环境变化、满意与信心。指南明确建议收窄到3—5个职业/专业/工作选项，改编自Sampson等1992文献。这是咨询练习经验，不是AI每批推荐3—5个最优的实证。迁移推断：实际接触与反馈可让用户返回前面的了解/比较阶段，不必只进不退。 [MAIN-CFSU](https://career.fsu.edu/students/career/planning/decision-making/guide-to-good-decision-making)

## D. 长期保存求职信息的合规要点

以下仅列法律原文要点及草稿差距，不作法律意见，也不替运营者决定合法基础或确认合同。

| 要点 | 内容与适用边界 | 证据 |
|---|---|---|
| 告知与同意 | 专业、经历、求职进展若能关联个人，属于个人信息。新增跨会话画像用途须事前清楚告知类别、目的、方式、期限和权利入口；按第13条确定合法基础，采用同意时遵守第14—16条，目的/方式/类别变化需重新同意。单纯长期保存普通信息不自动要求法定单独同意。 | [D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |
| 单独同意适用条件 | 向另一独立处理者提供、公开、敏感信息、跨境等场景分别受第23/25/29/39条约束；教育经历不当然是敏感信息，简历中健康、金融等内容须另行识别。 | [D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |
| 最短期限与权利 | 第19条要求必要最短期限；第44—50条覆盖查阅、复制、更正、删除、限制及便捷受理，不能仅以前端隐藏代替删除。依法保留期间按第47条限制后续处理。 | [D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |
| 删除执行与账号注销 | 条例第23—24条要求及时受理并提供便捷途径；注销、非必要或未依法同意信息应删除/匿名化。工程落实需覆盖原文、派生画像、索引、受托副本和备份生命周期；这是实施推断，不是法条列出的数据库清单。 | [D04](https://www.cac.gov.cn/2024-09/30/c_1729384452307680.htm)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |
| 六个月留存边界 | 暂行办法第11条不要求一律保存完整对话六个月；网络安全法现行第23条第三项要求相关网络日志不少于六个月。不能由此直接推得所有对话、画像、求职进展统一六个月；具体其他留存义务未作穷尽性审查。 | [D02](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)；[D03](https://www.cac.gov.cn/2025-12/29/c_1768735112911946.htm) |
| 自动化画像与推送 | PIPL第24条要求自动化决策透明、公平及适用情形下的拒绝/说明；条例第42条要求适用网络平台的信息推送可关闭个性化推荐、删除用户标签。是否覆盖小谷具体功能须结合最终行为判断。 | [D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)；[D04](https://www.cac.gov.cn/2024-09/30/c_1729384452307680.htm) |
| 委托与跨境 | 第21条的委托处理需约定并监督；第23条对独立接收方另有告知/单独同意。草稿对DeepSeek的角色仍待核实，不能由“调用API”直接定性。选境外云记忆须另审第38—39条，未核验实际跨境链路。 | [D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)；[L01](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html) |
| 内部评估 | 自动化决策、敏感信息、委托/提供/跨境等符合第55条情形时需事前个人信息保护影响评估；结果及记录按第56条至少保留三年。该期限针对评估记录，不等于全部用户对话。 | [D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |

### 对照现有隐私政策草稿

草稿的只读快照编号L01；以下“缺项”是文本审查结果，未检查代码是否已经提供相应能力。

| 对应位置 | 缺少或待核实事项 | 证据 |
|---|---|---|
| 第一、二节：记忆用途 | 缺独立列明跨会话画像、从对话抽取的偏好/阶段/投递进展，以及以后推荐、复盘如何使用；“提供和改进服务”不足以让用户理解新增范围。 | [L01](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |
| 第四节：分项期限 | 缺聊天、画像、投递事件、推荐批次、复盘推断、网络日志分别的期限/触发条件；“保存到删除为止”缺主动到期机制；统一6个月依据未证实。 | [L01](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)；[D02](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)；[D03](https://www.cac.gov.cn/2025-12/29/c_1768735112911946.htm) |
| 第五节：控制与派生数据 | 已有删除聊天和人工更正/导出/注销承诺，尚缺独立记忆的查看/改删、关闭记忆、撤回同意和限制处理方法，以及来源删除后派生副本处理边界；15工作日是草稿承诺，不是本次查得的PIPL统一法定期限。 | [L01](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)；[D04](https://www.cac.gov.cn/2024-09/30/c_1729384452307680.htm) |
| 第三节：接收方 | 缺落实受托/独立处理角色、保留期限、删除同步、是否用于训练及用户行权渠道；实际合同和数据流未核验，不能补造。 | [L01](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |
| 自动化推荐说明 | 缺何种画像影响方向排序、适用时的关闭个性化/标签删除/拒绝仅自动化重大决定入口。 | [L01](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)；[D04](https://www.cac.gov.cn/2024-09/30/c_1729384452307680.htm) |
| 运营者及例外 | 运营主体、日期、联系方式仍占位；未区分一般求职信息与敏感/未满14岁信息及对应机制；“未满18须监护人同意”不替代未满14专门规则。 | [L01](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) |

## 对设计的影响（证据导出的待选约束）

本节为研究迁移推断，供设计方决策；本轮没有确定Schema、默认开关、保存期限、技术栈或批次数，也没有实施。

| 影响 | 证据与推断 |
|---|---|
| 记忆类别及真值边界 | 推断：至少区分用户确认的基础事实/约束、偏好及其时间、实际行动与反馈事件、助手给过的批次记录、复盘假设。职业资料库和活动时间线支持前三类；论文反思可借来解释事件，但不应把推断升级为用户事实。底层是否分表本轮不决定。 [FOREIGN-TEAL](https://www.tealhq.com/pro)；[FOREIGN-HUNTR](https://huntr.co/product/job-tracker)；[MAIN-B05](https://arxiv.org/html/2304.03442v1)；[oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py) |
| 谁决定记 | 推断：事实写入依据应能追到用户原话或用户维护资料；模型自动提取可以作为候选写入机制，信息矛盾/身份关键项宜让用户纠正或确认，规则由设计方确定。Teal允许用户选择保存，通用助手也有自动选择路径，证据没有证明其中一种普遍最佳。不可照搬LLM抽取即真值。 [FOREIGN-TEAL](https://www.tealhq.com/pro)；[DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space)；[MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt)；[oss-mem0-source-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/main.py) |
| 用户查看、修改、删除 | 推断：需要独立于聊天列表的记忆查看和改删能力，显示来源/时间；关闭使用和删除数据分别说明。删除原聊天时派生画像/复盘/索引如何处理必须明确。通用助手已有独立控制，法条要求用户行权；界面具体实现本轮不定。 [MAIN-A09](https://help.openai.com/en/articles/8590148-memory-in-chatgpt)；[FOREIGN-CLAUDE](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context)；[DOM-KIMI-MEM](https://www.kimi.com/help/features/memory-space)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)；[D04](https://www.cac.gov.cn/2024-09/30/c_1729384452307680.htm) |
| 分批推进要记住的状态 | 推断：应能还原当前阶段、每批方向及当时依据、已经展示的方向、待验证问题、用户实际看JD/咨询/投递/面试的事件、反馈理由及时间、待等用户回复事项、下一轮调整依据。未行动、未反馈、明确否定、无回音分开；单一current_stage字符串或不断改写总摘要不足以复原过程。字段/状态机/批次数本轮不定。 [FOREIGN-HUNTR](https://huntr.co/product/job-tracker)；[DOM-ZH-AI](https://ai.zhaopin.com/)；[MAIN-CFSU](https://career.fsu.edu/students/career/planning/decision-making/guide-to-good-decision-making)；[FOREIGN-BANDIT](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/p661.pdf)；[oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py) |
| 可以直接复用的存储组件 | 条件推断：若约束为现有Python服务、单机SQLite且暂不需要知识图谱，当前LangGraph SqliteStore可复用为持久数据组件，具有JSON namespace/key、可选index与TTL；不是可直接部署的完整职业记忆功能。schema、用户隔离、抽取/纠错、并发与迁移都需另实现验证；本轮未装库、未跑部署。 [oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py)；[oss-langgraph-source-4](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py)；[oss-langgraph-verify-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/pyproject.toml) |
| 借思路与当前约束下不适合 | 条件推断：mem0可借挑选抽取/关联检索，但仅SQLite要求下不能原样直接用，中文spaCy问题及默认境外模型需处理；Letta可借核心/按需/反思和可追溯编辑，但现行Node/Git实现不适合作为Python+SQLite即插即用；Graphiti可借时间失效与事件来源，若仅需个人事实/批次记录，其图后端与LLM流程超出轻量约束。这里评估的是部署契合度，不是产品优劣。 [oss-mem0-source-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/configs/base.py)；[oss-mem0-verify-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/utils/spacy_models.py)；[oss-mem0-issue-4884](https://api.github.com/repos/mem0ai/mem0/issues/4884)；[oss-letta-readme](https://raw.githubusercontent.com/letta-ai/letta/5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a/README.md)；[oss-letta-extra-4](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/subagents/builtin/reflection-v2.md)；[oss-letta-extra-7](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/transcript-search.ts)；[oss-graphiti-readme](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/README.md)；[oss-graphiti-extra-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/prompts/dedupe_edges.py) |
| 反馈与复盘 | 推断：每一轮真实行动后回看具体未知是否减少，保留新方向探索机会；复盘结论指向当时事件和证据，并标可修正的解释。没有回音不能直接定为人岗不合，没投也不能定为不喜欢；用不了充分反馈时不应假装统计学习已收敛。论文反思会漏检或虚构，因此总结不替代原始事件。 [FOREIGN-STANFORD](https://lifedesignlab.stanford.edu/s/June-Virtual-2024-Studio-Day-2-compressed.pdf)；[MAIN-CFSU](https://career.fsu.edu/students/career/planning/decision-making/guide-to-good-decision-making)；[FOREIGN-BANDIT](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/p661.pdf)；[MAIN-B05](https://arxiv.org/html/2304.03442v1) |
| 数量与保存期限的决定仍需验证 | 推断：3—5个职业选项和三条人生路径可作可解释的经验参照；每批几个需看用户是否能获得并反馈真实信息，不写成科学最优。长期保存功能上线前应落实告知、最短期限及派生数据删除，尤其不能以网络日志六个月替代所有记忆的必要性判断。 [MAIN-CFSU](https://career.fsu.edu/students/career/planning/decision-making/guide-to-good-decision-making)；[FOREIGN-STANFORD](https://lifedesignlab.stanford.edu/s/June-Virtual-2024-Studio-Day-2-compressed.pdf)；[D01](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm)；[D02](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm)；[D03](https://www.cac.gov.cn/2025-12/29/c_1768735112911946.htm) |

## 对brief事前判断的对账

| 事前判断 | 本次证据允许的对账 |
|---|---|
| 国内主要记结构化简历；基本没有对话记忆；反馈靠行为 | 智联和超级简历政策支持简历及行为画像。国内职业样本AI对话记忆缺少正文，不能据此支持“基本没有”；Kimi对照明确有跨会话记忆。也未核实国内AI反馈主要来自哪一类。 |
| Python+SQLite且不依赖境外不超过2个，多数默认向量库/OpenAI | 见B按固定commit和可选配置对照；“仅Python+SQLite”必须包含是否本地推理/embedding、向量扩展与持久化。未部署运行，不能给跨方案数量普遍结论；不以可配置选项否定默认依赖。 |
| 每批方向没有实证，只有经验 | 本轮未找到每批最优数量实证；找到Stanford三条路径与FSU 3—5职业选项经验。未找到只针对本次检索范围。 |

## 证据索引与取证层级

一级：官方产品说明、官方仓库/源码、作者论文与主管部门法条；二级：媒体/第三方原创（本次搜索线索另标）；三级：论坛/用户反馈，仓库Issue中用户体验也属三级。0为只读本地材料。来源层级与正文状态是两个字段：官方搜索摘要仍不是正文。

正文快照分为原HTML/PDF/固定commit源码与web工具提取返回，不是浏览器截图，不保证完整视觉布局。搜索输出、robots、错误页只证明检索/访问边界。SHA256核验完整性，不核验功能或结论。主批次和分册脚本保留限速/robots日志；遇到空正文、访问拒绝或未知robots不以换登录态绕过。

采集审计：首轮GitHub多仓库web侦察未先核robots，工具未暴露请求时刻，无法证明每站间隔≥3秒；这些首轮输出未用于B结论。后续B引用源用robots前置、3.1秒脚本取得，不能反向把首轮改标合规。Wiley在取得官方摘要后补查robots才发现GPTBot禁令，立即停止；该条不作全文依据。主Agent部分web侦察/正文工具也不能以工具耗时证明实际请求间隔，后续Python批次保留3.2秒限速记录。ChatGPT说明/套餐原始HTML抓取403，未做登录或浏览器重试，只保留已取得的公开web提取返回；这不等于本机原始网页抓取成功。审计文件oss-acquisition-audit.json、foreign-fetch-manifest.json、main-fetch/manifest.json随证据保留。故本次不宣称全程采集协议验收通过。

机器可读完整索引：[sources.json](../../evidence/memory-journey-2026-10/sources.json)；全部文件校验：[checksums.json](../../evidence/memory-journey-2026-10/checksums.json)。CSV为UTF-8长表，一行一个问题/结论；证据数组是JSON单元格，sha按同序对齐。

| 编号 | 来源URL/标题 | 等级 | 访问日期 | 短摘 | 取证状态 |
|---|---|---|---|---|
| DOM-BOSS-OLD | [BOSS直聘用户协议及隐私政策（2019旧版）](https://www.zhipin.com/web/common/protocol/protocol-2019-01-28.html) | 1 | 2026-10-14 | 完善微简历或者职位介绍 | body-old |
| DOM-BOSS-HOME | [BOSS直聘公开首页](https://www.zhipin.com/) | 1 | 2026-10-14 | 感兴趣 | public-body |
| DOM-BOSS-2025-LEAD | [2025 ESG Report（仅发现线索）](https://ir.zhipin.com/system/files-encrypted/nasdaq_kms/assets/2026/04/29/9-28-11/2025%20Annual%20ESG%20Report%20%28CN%29.pdf) | 1 | 2026-10-14 | 春招AI 助手 | discovery-only-robots-timeout |
| DOM-ZH-AI | [智联求职AI公开预约页](https://ai.zhaopin.com/) | 1 | 2026-10-14 | 集中查看投递、沟通和待处理事项 | official-marketing-body |
| DOM-ZH-PRIV | [智联招聘隐私政策2025 V2](https://img01.zhaopin.com/2012/other/mobile/legal/protocol/2025/%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98%E9%9A%90%E7%A7%81%E6%94%BF%E7%AD%96_2025V2.pdf) | 1 | 2026-10-14 | 求职意向：期望职位、期望行业 | body-old-policy |
| DOM-ZH-CONTROL | [智联2025 V2信息管理条款](https://img01.zhaopin.com/2012/other/mobile/legal/protocol/2025/%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98%E9%9A%90%E7%A7%81%E6%94%BF%E7%AD%96_2025V2.pdf) | 1 | 2026-10-14 | 我的简历 | body-old-policy |
| DOM-NC-HOME | [牛客公开首页](https://www.nowcoder.com/home/) | 1 | 2026-10-14 | 简历助手 一键闪填网申简历 | public-body |
| DOM-NC-EMPTY | [牛客网申助手入口](https://www.nowcoder.com/my/resume-plugin-intro) | 1 | 2026-10-14 | 无（未取得目标正文或仅检索） | empty-target-body-stopped |
| DOM-WCV-PRIV | [超级简历隐私条款（2021-12-03）](https://www.wondercv.com/newPrivacy) | 1 | 2026-10-14 | 工作经历、职业技能 | body-old-policy |
| DOM-WCV-CONTROL | [超级简历信息管理条款](https://www.wondercv.com/newPrivacy) | 1 | 2026-10-14 | 删除个人资料及个人账户相关信息 | body-old-policy |
| DOM-WCV-PRICE | [超级简历限时优惠公开页](https://www.wondercv.com/jianlimoban/xianshiyouhui/) | 1 | 2026-10-14 | 开通超级会员，尊享6大特权 | public-body |
| DOM-KIMI-MEM | [Kimi记忆空间介绍](https://www.kimi.com/help/features/memory-space) | 1 | 2026-10-14 | 个人主页 → 设置 → 记忆指令 | official-help-body |
| DOM-KIMI-PRICE | [Kimi会员订阅](https://www.kimi.com/help/membership) | 1 | 2026-10-14 | 无（未取得目标正文或仅检索） | public-page-unresolved |
| FOREIGN-TEAL | [Teal Pro — Your career, remembered and working for you](https://www.tealhq.com/pro) | 1 | 2026-10-14 | You choose what gets saved. | body_verified |
| FOREIGN-TEAL-PRICE | [Teal+ Pricing](https://www.tealhq.com/pricing) | 1 | 2026-10-14 | Free Forever | body_verified |
| FOREIGN-CF | [Careerflow official homepage](https://www.careerflow.ai/) | 1 | 2026-10-14 | Job Tracker | body_verified |
| FOREIGN-HUNTR | [Job Application Tracker](https://huntr.co/product/job-tracker) | 1 | 2026-10-14 | Track Activities | body_verified |
| FOREIGN-HUNTR-PRICE | [Huntr Pricing Plans](https://huntr.co/pricing) | 1 | 2026-10-14 | Advanced Job Search Metrics | body_verified |
| FOREIGN-CLAUDE | [Use Claude’s chat search and memory to build on previous context](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context) | 1 | 2026-10-14 | individual topics | body_verified |
| FOREIGN-STANFORD | [Life Design Studio, June Virtual 2024, Day 2](https://lifedesignlab.stanford.edu/s/June-Virtual-2024-Studio-Day-2-compressed.pdf) | 1 | 2026-10-14 | PROTOTYPE CONVERSATIONS | body_verified |
| FOREIGN-BANDIT | [A Contextual-Bandit Approach to Personalized News Article Recommendation (WWW 2010)](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/p661.pdf) | 1 | 2026-10-14 | user-click feedback | body_verified |
| FOREIGN-LI-STOP | [LinkedIn robots access restriction](https://www.linkedin.com/robots.txt) | 1 | 2026-10-14 | express permission | robots_stop_no_product_body |
| FOREIGN-PLANNED | [Planned Happenstance: Constructing Unexpected Career Opportunities (1999)](https://onlinelibrary.wiley.com/doi/10.1002/j.1556-6676.1999.tb02431.x) | 1 | 2026-10-14 | exploratory activities | public_abstract_read_before_robots_check_then_stop; full_text_not_read |
| FOREIGN-NUMBER-SEARCH | [Career-direction-count discovery record: Graduates’ career choices (search hit, body not read)](https://link.springer.com/article/10.1007/s10775-024-09720-4) | 3 | 2026-10-14 | 无（未取得目标正文或仅检索） | discovery_only_not_body_evidence; URL_is_search_hit_not_fetched_page |
| oss-graphiti-comments-312 | [oss-graphiti-comments-312](https://api.github.com/repos/getzep/graphiti/issues/312/comments) | 3 | 2026-10-14 | Looking forward to it! | 正文已读/源码静态核验 |
| oss-graphiti-commit | [oss-graphiti-commit](https://api.github.com/repos/getzep/graphiti/commits/HEAD) | 1 | 2026-10-14 | 无（未取得目标正文或仅检索） | 正文已读/源码静态核验 |
| oss-graphiti-extra-1 | [oss-graphiti-extra-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/prompts/dedupe_edges.py) | 1 | 2026-10-14 | contradicted_facts | 正文已读/源码静态核验 |
| oss-graphiti-issue-312 | [oss-graphiti-issue-312](https://api.github.com/repos/getzep/graphiti/issues/312) | 3 | 2026-10-14 | mixed with English | 正文已读/源码静态核验 |
| oss-graphiti-readme | [oss-graphiti-readme](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/README.md) | 1 | 2026-10-14 | Kuzu is **deprecated** | 正文已读/源码静态核验 |
| oss-graphiti-source-1 | [oss-graphiti-source-1](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/graphiti.py) | 1 | 2026-10-14 | store_raw_episode_content | 正文已读/源码静态核验 |
| oss-graphiti-source-2 | [oss-graphiti-source-2](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/graphiti_core/llm_client/config.py) | 1 | 2026-10-14 | base_url | 正文已读/源码静态核验 |
| oss-graphiti-source-3 | [oss-graphiti-source-3](https://raw.githubusercontent.com/getzep/graphiti/8d8a12a22452cbef9335792afb73b8cbfe6a79fa/LICENSE) | 1 | 2026-10-14 | Apache License | 正文已读/源码静态核验 |
| oss-langgraph-commit | [oss-langgraph-commit](https://api.github.com/repos/langchain-ai/langgraph/commits/HEAD) | 1 | 2026-10-14 | 无（未取得目标正文或仅检索） | 正文已读/源码静态核验 |
| oss-langgraph-issue-8514 | [oss-langgraph-issue-8514](https://api.github.com/repos/langchain-ai/langgraph/issues/8514) | 3 | 2026-10-14 | UnicodeDecodeError | 正文已读/源码静态核验 |
| oss-langgraph-source-1 | [oss-langgraph-source-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/base/__init__.py) | 1 | 2026-10-14 | JSON-serializable values | 正文已读/源码静态核验 |
| oss-langgraph-source-2 | [oss-langgraph-source-2](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint/langgraph/store/memory/__init__.py) | 1 | 2026-10-14 | Data is lost | 正文已读/源码静态核验 |
| oss-langgraph-source-4 | [oss-langgraph-source-4](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py) | 1 | 2026-10-14 | INSERT OR REPLACE INTO store | 正文已读/源码静态核验 |
| oss-langgraph-source-5 | [oss-langgraph-source-5](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/LICENSE) | 1 | 2026-10-14 | MIT License | 正文已读/源码静态核验 |
| oss-langgraph-verify-1 | [oss-langgraph-verify-1](https://raw.githubusercontent.com/langchain-ai/langgraph/a6731f436700c7d46a9224ccd3a0e0ce3a5bfdb5/libs/checkpoint-sqlite/pyproject.toml) | 1 | 2026-10-14 | sqlite-vec | 正文已读/源码静态核验 |
| oss-letta-commit | [oss-letta-commit](https://api.github.com/repos/letta-ai/letta/commits/HEAD) | 1 | 2026-10-14 | 无（未取得目标正文或仅检索） | 正文已读/源码静态核验 |
| oss-letta-extra-1 | [oss-letta-extra-1](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/LICENSE) | 1 | 2026-10-14 | Apache License | 正文已读/源码静态核验 |
| oss-letta-extra-3 | [oss-letta-extra-3](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/local-store.ts) | 1 | 2026-10-14 | appendFileSync | 正文已读/源码静态核验 |
| oss-letta-extra-4 | [oss-letta-extra-4](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/subagents/builtin/reflection-v2.md) | 1 | 2026-10-14 | Core memory | 正文已读/源码静态核验 |
| oss-letta-extra-5 | [oss-letta-extra-5](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/agent/memory-conflict-repair.ts) | 1 | 2026-10-14 | could not resolve it | 正文已读/源码静态核验 |
| oss-letta-extra-6 | [oss-letta-extra-6](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/system-prompt-compilation.ts) | 1 | 2026-10-14 | if (!revision) | 正文已读/源码静态核验 |
| oss-letta-extra-7 | [oss-letta-extra-7](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/src/backend/local/transcript-search.ts) | 1 | 2026-10-14 | Use "fts". | 正文已读/源码静态核验 |
| oss-letta-issue-2644 | [oss-letta-issue-2644](https://api.github.com/repos/letta-ai/letta-code/issues/2644) | 3 | 2026-10-14 | IME candidate selection window | 正文已读/源码静态核验 |
| oss-letta-readme | [oss-letta-readme](https://raw.githubusercontent.com/letta-ai/letta/5bcdd177d70fa2b31a754cfcd801e77b2e1ab16a/README.md) | 1 | 2026-10-14 | retired Letta V1 API server | 正文已读/源码静态核验 |
| oss-lettacode-commit | [oss-lettacode-commit](https://api.github.com/repos/letta-ai/letta-code/commits/HEAD) | 1 | 2026-10-14 | 无（未取得目标正文或仅检索） | 正文已读/源码静态核验 |
| oss-lettacode-verify-1 | [oss-lettacode-verify-1](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/README.md) | 1 | 2026-10-14 | Letta Cloud is the default. | 正文已读/源码静态核验 |
| oss-lettacode-verify-2 | [oss-lettacode-verify-2](https://raw.githubusercontent.com/letta-ai/letta-code/c76fd84a61d64cfd3d9a9730205f67bd4230c818/package.json) | 1 | 2026-10-14 | "engines" | 正文已读/源码静态核验 |
| oss-mem0-commit | [oss-mem0-commit](https://api.github.com/repos/mem0ai/mem0/commits/HEAD) | 1 | 2026-10-14 | 无（未取得目标正文或仅检索） | 正文已读/源码静态核验 |
| oss-mem0-extra-1 | [oss-mem0-extra-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/vector_stores/configs.py) | 1 | 2026-10-14 | default="qdrant" | 正文已读/源码静态核验 |
| oss-mem0-extra-2 | [oss-mem0-extra-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/vector_stores/qdrant.py) | 1 | 2026-10-14 | BM25 keyword scoring | 正文已读/源码静态核验 |
| oss-mem0-extra-3 | [oss-mem0-extra-3](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/configs/prompts.py) | 1 | 2026-10-14 | use_input_language=False | 正文已读/源码静态核验 |
| oss-mem0-extra-4 | [oss-mem0-extra-4](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/telemetry.py) | 1 | 2026-10-14 | MEM0_TELEMETRY | 正文已读/源码静态核验 |
| oss-mem0-issue-4884 | [oss-mem0-issue-4884](https://api.github.com/repos/mem0ai/mem0/issues/4884) | 3 | 2026-10-14 | BM25 silently becomes a no-op. | 正文已读/源码静态核验 |
| oss-mem0-pr-6718 | [oss-mem0-pr-6718](https://api.github.com/repos/mem0ai/mem0/pulls/6718) | 3 | 2026-10-14 | Empty BM25 text | 正文已读/源码静态核验 |
| oss-mem0-readme | [oss-mem0-readme](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/README.md) | 1 | 2026-10-14 | ADD-only extraction | 正文已读/源码静态核验 |
| oss-mem0-source-1 | [oss-mem0-source-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/memory/main.py) | 1 | 2026-10-14 | # === V3 PHASED BATCH PIPELINE | 正文已读/源码静态核验 |
| oss-mem0-source-2 | [oss-mem0-source-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/configs/base.py) | 1 | 2026-10-14 | Path to the history database | 正文已读/源码静态核验 |
| oss-mem0-source-3 | [oss-mem0-source-3](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/LICENSE) | 1 | 2026-10-14 | Apache License | 正文已读/源码静态核验 |
| oss-mem0-source-4 | [oss-mem0-source-4](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/docs/cookbooks/companions/local-companion-ollama.mdx) | 1 | 2026-10-14 | Self-Hosted AI Companion | 正文已读/源码静态核验 |
| oss-mem0-verify-1 | [oss-mem0-verify-1](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/utils/spacy_models.py) | 1 | 2026-10-14 | en_core_web_sm | 正文已读/源码静态核验 |
| oss-mem0-verify-2 | [oss-mem0-verify-2](https://raw.githubusercontent.com/mem0ai/mem0/d26ba5e4518cef7fff3c66d4f715b21adf9feabe/mem0/utils/lemmatization.py) | 1 | 2026-10-14 | token.lemma_ | 正文已读/源码静态核验 |
| D01 | [个人信息保护法（2021通过/施行）](https://www.cac.gov.cn/2021-08/20/c_1631050028355286.htm) | 1 | 2026-10-14 | 实现处理目的所必要的最短时间 | 正文已核验 |
| D02 | [生成式人工智能服务管理暂行办法（2023施行）](https://www.cac.gov.cn/2023-07/13/c_1690898327029107.htm) | 1 | 2026-10-14 | 不得收集非必要个人信息 | 正文已核验 |
| D03 | [网络安全法（2025修正，2026施行）](https://www.cac.gov.cn/2025-12/29/c_1768735112911946.htm) | 1 | 2026-10-14 | 相关的网络日志不少于六个月 | 正文已核验 |
| D04 | [网络数据安全管理条例（2025施行）](https://www.cac.gov.cn/2024-09/30/c_1729384452307680.htm) | 1 | 2026-10-14 | 删除针对其个人特征的用户标签 | 正文已核验 |
| L01 | [小谷隐私草稿（只读本地）](/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/web/static/legal-privacy.html) | 0 | 2026-10-14 | 相关记录会在后台继续留存不少于 6 个月 | 正文已核验 |
| MAIN-A09 | [Memory in ChatGPT](https://help.openai.com/en/articles/8590148-memory-in-chatgpt) | 1 | 2026-10-14 | separately from chat history | 正文已核验 |
| MAIN-A09P | [ChatGPT公开套餐页](https://openai.com/chatgpt/pricing/) | 1 | 2026-10-14 | Limited memory and context | 正文已核验 |
| MAIN-B05 | [Generative Agents (2023, arXiv v1)](https://arxiv.org/html/2304.03442v1) | 1 | 2026-10-14 | more abstract thoughts | 正文已核验 |
| MAIN-CFSU | [FSU Career Center：CASVE决策指南（改编自1992文献）](https://career.fsu.edu/students/career/planning/decision-making/guide-to-good-decision-making) | 1 | 2026-10-14 | 3 to 5 best occupations | 正文已核验 |

## 验收清单

- A：11产品，共66问；国内职业4、国外职业4、通用对照3。逐项有证据或未能确认。
- B：4开源方案×6问，固定版本/commit；反思论文1项。
- C：Stanford与FSU两套完整公开方法，另有计划性偶发摘要记录、探索利用原论文、数量经验及实证缺口。
- D：合规要点与隐私草稿缺项逐条列出。
- E：所有设计影响指回证据，不作实施决定。
- 快照/引用/CSV结构由validator核验；独立审阅结果见同目录memory-journey-2026-10-review.md；不把形式校验通过当语义完整或Claude验收通过。
- 部分验收缺口：LinkedIn、BOSS 2025正文、牛客目标正文、登录界面/实际闭环、部署运行与中文精度。没有授权绕过的恢复路径；后续只补新增公开正文或用户提供的授权材料。
