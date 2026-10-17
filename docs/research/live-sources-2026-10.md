# 岗位理解实时来源调研（部分验收）

访问：2026-10-04至10-05，Asia/Shanghai。事实、厂商自述、推断与未完成项分别标注。原始目标为Q1–Q6；本文不能代替所有验收通过。历史报告备份于tasks/research-2026-10/evidence/live-sources-report-2026-10-04.md。

## 当前判断

CDP已恢复，实际页面正文和截图证明连接有效；没有Chrome弹窗不构成阻塞。公开产品可核验的主流程以JD匹配、简历优化、模拟面试、投递管理为主。未找到它们默认以可追溯员工日常分享解释岗位的证据；这不证明它们绝对没有此能力。

建议小谷先将“JD原文、招聘方主张、员工个人分享、模型解释”分栏并各自保留来源，员工信息不足时显示未知。牛客公开详情部分可读，但服务条款未取得、面经有付费截断，不能据robots直接启用生产抓取。API候选已取得官方价格与功能资料，中文搜索质量尚无实际调用数据，因此选型仍暂定。

## Q1 已有功能地图

国内八个求职工具/平台、海外两个，满足工具观察数量；其中BOSS、猎聘的AI岗位理解能力未验证。访问日见证据清单；10-04读取效招、牛客AI、BOSS、Teal、Jobscan，10-05其余。只观察公开页面，不注册、启动面试、自动投递或发消息。

| 产品与来源 | 已有功能/信息来源 | 来源与日期 | 招聘方与员工分层 | 失败/降级与限制 |
|---|---|---|---|---|
| [效招Joblytic](https://xzjobs.cn/products/job-board) | 公开岗位看板演示JD信号、个人经历匹配、问招招；第三方社区来源未披露 | 演示没有逐项引用或发帖日期 | 未找到员工日常分层 | 只核验演示；没有登录后真实失败测试，不能把示例职位数当数据库体量 |
| [牛客AI](https://www.nowcoder.com/interview/ai/index) | 自有题库分类、公司/岗位模拟面试入口；同站UGC存在，但未证明AI答案取自UGC | 真题年份与公司可见；AI答案级引用未找到 | 未找到明确分层 | 需要登录启动体验；另有面经付费截断证据 |
| [BOSS直聘](https://www.zhipin.com/) | 招聘职位、公司规模/融资信息 | 招聘方卡片，不是AI答案来源证据 | 未找到 | 首页自动跳城市页；内置AI入口与答案未核验 |
| [超级简历](https://www.wondercv.com/) | 厂商称行业语料、表达模型、JD解析；AI生成/检查/定制简历 | 未找到答案级外部引用、员工帖子日期 | 未找到 | 免费使用CTA到登录；人类顾问189元起不等于AI价格 |
| [智联招聘/智联求职AI版](https://ai.zhaopin.com/) | 招聘数据库及厂商演示筛岗、改简历、代聊；关键薪资/时间答复由用户确认是页面自述 | 演示未展示员工日常引用及日期 | 招聘信息，未找到员工说法 | 首页邀请体验/限量内测文案，不证明当前免登录可操作；没有发送消息 |
| [猎聘](https://www.liepin.com/) | 招聘方职位正文、公司属性，简历优化服务入口 | JD与公司卡片可核验；发帖日期未找到 | 正文来自招聘方，不能作为员工反馈 | 登录/聊一聊入口存在，但公开JD可读；AI岗位解释未验证 |
| [Teal](https://www.tealhq.com/) | 厂商称收藏40多个招聘网站职位、JD关键词匹配与求职管理 | 招聘网站来源概念可见；答案级日期未找到 | 未找到 | 首页注册引导；6倍面试等效果是厂商自述，未独立验证 |
| [Jobscan](https://www.jobscan.co/) | 简历与用户输入JD的ATS匹配，厂商称其有专有分析 | 输入JD是材料；外部员工引用/日期未找到 | 未找到 | 注册/扫描引导，实际扫描失败未测；效果提升为厂商自述 |

10-05经web-access公开静态读取补充：

| 产品/原文 | 功能与信息源 | 日期/员工分层 | 失败/限制 |
|---|---|---|---|
| [职徒52cv](https://www.52cv.com/) | 官网自述AI简历评分、简历/JD生成面试题、模拟面试与反馈、职业规划；社区入口存在但未证明AI取自UGC | 答案级来源、员工分层、日期未找到 | 只核验公开页面；robots静态请求无法读取，不深入交互，不宣称免费额度；“通过率翻倍”仅厂商自述 |
| [知页](https://www.zhiyeapp.com/) | 既有主页证据与公开索引均提AI简历诊断、模板/智能填写 | 厂商材料，未证明员工引用/答案日期 | 仍未核验AI实际工作台/配额；robots先前跳主页不能当有效规则 |

多面鹅候选域名未确认且请求曾ERR_CONNECTION_CLOSED；不列为已验证产品。先前职徒候选域名不可靠，本轮找到52cv官网；不采用zhitujianli.com自称官网且带占位客服号码的页面。看准当前页面是婚恋平台，不用旧求职定位凑数量。

**推断**：市场差异应验证为“可追溯员工信息能否改善用户理解与决策”，不能由竞品首页没写此功能推出差异成立。需要用户阅读、继续追问、决策纠偏等实测，暂无因果效果证据。

## Q2 牛客详情可读性

| 实测样本 | 公开范围、日期和标签 | 尚未证明 |
|---|---|---|
| [暑期实习刷题程度](https://www.nowcoder.com/feed/main/detail/085f500846374269af6c3b75b9d0b9ac) | 10-04显示登录/注册，标题及两句正文可读；145浏览、3评论；“昨天22:56、已编辑”，自填Java | 10-05无Cookie原始HTTP200，DOMParser不执行脚本即取得相同标题与两句正文；自填标签不是在职认证 |
| [超聚变嵌入式二面](https://www.nowcoder.com/discuss/934495940616998912?sourceSSR=home) | 09-29 17:13；DOM有公开内容，截图有登录遮罩；页面明确剩余60%需订阅/购买 | 不能称全篇可读或用户无阻碍；不是算法岗位日常样本 |

早期保存的page.html是执行后的DOM，不是原始HTTP HTML。10-05另通过CDP页面内fetch(credentials:omit)读取原始响应，以不执行脚本的DOMParser提取.feed-content-text；该刷题样本正文已在原始HTML中，支持其SSR可读。证据evidence/live-sources-2026-10/nowcoder-http-body.json保存正文及原始HTML片段。这不是curl或XiaoguBot UA测试，不能外推全部详情；另有页面仅页脚或“内容不存在”的失败样本。条款链接由首页取得：[注册协议](https://static.nowcoder.com/protocol/register.html)、[隐私政策](https://static.nowcoder.com/protocol/privacy-policy.html)。但[static域名robots](https://static.nowcoder.com/robots.txt)对*全站禁止，未访问协议正文。自动化、AI抓取、转载引用条款均无法确定；要求平台提供可合法读取的文本或授权接口，不能改UA绕过。

## Q3 发现路径

| 引擎 | 本次robots证据 | 两条固定查询的条数、前十详情率、新近度 |
|---|---|---|
| [百度](https://www.baidu.com/robots.txt) | *全站禁止 | skipped_robots，未执行，不能写0结果 |
| [必应](https://www.bing.com/robots.txt) | *禁/search与/Search | 未执行 |
| [搜狗](https://www.sogou.com/robots.txt) | 完整正文末尾*全站禁止 | 未执行 |
| [Google](https://www.google.com/robots.txt) | *禁普通/search | 未执行 |

不推荐其中某个引擎的质量排名；网页SERP与获得合同许可的API调用是不同路径，API必须独立测试。脉脉按最新Q4排除，不再测试。

[牛客根sitemap](https://www.nowcoder.com/sitemap.xml)仅列两个子文件，使用urlset；10-04 lastmod为2026-10-04T01:00:03.342+08:00。[sitemap1](https://www.nowcoder.com/sitemap1.xml)经CDP内credentials:omit的fetch取得HTTP200：4,808,775字符、20,739 URL、5,513 /discuss/；算法/推荐/面经关键词0。所有条目声明daily，但这不是实际每天更新的证明。sitemap2未测，不能推算全站体量；lastmod不等于首次发表日。证据tasks/research-2026-10/evidence/sitemap1-summary.json仅保存统计，完整XML没保存，独立审阅不能复算数字。

可用的另一发现入口已实测：[猎聘公开分类页](https://www.liepin.com/city-sh/zpdsjaigcsf1c6/)提供职位详情链接。仅发现当前样本，不代表岗位覆盖率；去掉追踪参数后访问被允许的详情路径。

## Q4 自有XiaoguBot候选规则

| 主机/规则原文 | *规则和详情判断 | 结论 |
|---|---|---|
| [www.nowcoder.com](https://www.nowcoder.com/robots.txt) | 禁/search、/nccommon、/ab/ab-test-flow；讨论详情未禁止 | 可做有限公开可访问性研究；条款许可未确认 |
| [static.nowcoder.com](https://static.nowcoder.com/robots.txt) | 禁/ | 不访问协议正文 |
| [www.kanzhun.com](https://www.kanzhun.com/robots.txt) | 跳到婚恋主页，没有有效规则 | 无法确定，不启用 |
| [zhuanlan.zhihu.com](https://zhuanlan.zhihu.com/robots.txt) | 禁/，仅允许/tardis/jm | 不抓普通/p/，不利用例外绕路 |
| [www.yingjiesheng.com](https://www.yingjiesheng.com/robots.txt) | 禁cache/datatemp/includes/toolkit/attachments/maintenance/emailfriend.php | 其他详情不在该规则禁止范围；BBS须另核验，条款未知 |
| 脉脉 | 最新brief给定*全站禁止，无需再测 | 排除；不冒用宿主UA |
| [www.liepin.com](https://www.liepin.com/robots.txt) | 禁用户、活动、验证码、带查询参数及部分API | 本次只读无查询公开职位正文；不据此推断商业转载许可 |
| [www.zhaopin.com](https://www.zhaopin.com/robots.txt) | 禁用户、来源、全部查询、API等 | 首页明确未经同意不得转载全部招聘信息及作品；不能忽略该限制 |

浏览器取robots不是已经用XiaoguBot发请求的证明。生产许可仍需“主机、路径、条款、用途”共同判断。

## Q5 五份真实算法JD

10-05已保存五份完整职位介绍与链接：evidence/live-sources-2026-10/jd-algorithm-1至5/jd-full.md，原页面cdp-page.json及截图同目录。发布日期均未找到；访问日不能当发帖日。规模来自招聘平台，不是独立公司人数核验。

| 公司/规模（平台标注） | 职位及原文 | 招聘方职责摘要 |
|---|---|---|
| 阶跃星辰，100–499人；公司简介自称2023成立的大模型创业公司 | [AI记忆算法工程师](https://www.liepin.com/job/1985645221.shtml) | 端侧多模态用户记忆、效果评估、跨团队工程落地；LLM/Agent、SFT/RL经验 |
| 紫光展锐，2000–5000人 | [AI算法开发工程师](https://www.liepin.com/job/1985643527.shtml) | 端侧推理SDK、模型转换部署、性能与精度优化 |
| 华住，10000人以上 | [搜索排序AI算法](https://www.liepin.com/job/1985632053.shtml) | 搜索排序业务；具体完整要求见保存原文 |
| 小鹏，10000人以上 | [AI底盘算法开发](https://www.liepin.com/job/1985628451.shtml) | 底盘控制算法；具体完整要求见原文 |
| 益海嘉里，2000–5000人 | [电气自动化AI算法](https://www.liepin.com/job/1985282145.shtml) | 工业控制、设备故障预测、数据整理、算法与PLC/DCS/SCADA集成 |

规模跨三档，但没有独立证明“中厂”的统一定义；创业属性是公司简介自述。岗位跨度大，不据五个不同算法子岗位推导统一日常占比。另保存SKF机器学习相邻JD作补充，不计入上述五份。

### 10-05 web-access补充的真实来源fixture

公开静态正文取得以下三篇，保存于examples/algorithm-engineer-real/live_sources.json。字段与mock一致，但不覆盖mock的full情景；没有替换旧mock。原文只做简短要点，身份、年份和业务范围明确保留未知。

| 原帖 | 页面日期/标签 | 能支持的内容与限制 |
|---|---|---|
| [智驾感知算法实习工作总结](https://www.nowcoder.com/discuss/677971054463053824) | 2024-10-21 20:14；智能驾驶系统工程师，正文自称实习1年9个月后正式 | 自述数据训练评测、难例反馈、接口实现与部署协助；按OKR推进、论文/mentor讨论。无时间百分比或绩效数值；目标若为推荐算法，属于different_team；身份未核验，旧帖 |
| [算法岗实习该干什么](https://www.nowcoder.com/feed/main/detail/d0cfcd0f756740069b64fe1956fc9b7f) | 2024-05-24 15:31；页面Java，正文自称算法实习两周 | 自述初期调研学习、氛围轻松而担心提升。标签不一致，公司未说，scope=unknown；评论只作不同体验旁证，不冒充主帖同团队 |
| [算法工程师的日常](https://www.nowcoder.com/feed/main/detail/bd84598eaf9745bdb3611dba5435ff12) | 页面01-07 11:56，年份未显示；自填算法工程师 | 自述晚间至约十点、周末看实验；含晚间指导业务。工作与副业需区分，商业动机及在职身份未核验，scope=unknown；不用来证明典型工时 |

四主题有定性材料，但日常占比、当前同团队工时、绩效门槛及身份仍缺。资料不是认证事实，未得到同公司来源，不给行业统一比例。evidence/live-sources-2026-10/web-access-supplement.json保存方法、来源和要点；静态提取结果有抓取缓存日期，访问日不等于抓取日，也不是本轮Chrome截图/原始HTTP响应。

新增两项真实fixture回归：字段/作用域/脉脉排除与真实引用renderer读取。完整python3 -m unittest discover -s tests通过70项；本机假服务监听需沙箱外许可，已获工具批准，无真实模型API。旧mock未改。测试只证明fixture兼容与话术标注，不能核验员工身份或来源事实。

## Q6 搜索API：官方文档比较，实际质量未测

以下访问日均10-05。固定五查询预注册在tasks/research-2026-10/search-test-queries.json。没有调用API、申请密钥、注册或扣费；结果质量、前十详情率、日期真实性、中文召回全部未测。不能用官方示例咖啡搜索冒充固定查询测试。

| 候选/官方来源 | site/域名、摘要与日期 | 价格/免费额度 | 限流与许可/主体 |
|---|---|---|---|
| [博查Web Search文档](https://bocha-ai.feishu.cn/wiki/RXEOw02rFiwzGSkd9mUcqoeAnNK)、[价格](https://bocha-ai.feishu.cn/wiki/JYSbwzdPIiFnz4kDYPXcHSDrnZb) | snippet、summary、datePublished；分页与时间范围可见；site限定完整参数未读到 | Web Search¥0.036/次，AI Search¥0.060/次；内测免费结束，资源包下部虚拟化内容尚未取全 | 首页1000–2000QPS是服务能力自述，不是账号限额；[协议](https://open.bochaai.com/terms-of-service)允许按API服务协议使用、禁止从服务擅自抓取；不能把API许可当源站转载许可；个人/组织均可注册的描述未发现国内主体强制条款，仍不能证明绝对没有 |
| [Tavily Search](https://docs.tavily.com/documentation/api-reference/endpoint/search)、[价格](https://docs.tavily.com/documentation/api-credits)、[限流](https://docs.tavily.com/documentation/rate-limits) | include_domains≤300（restrict或prefer）；默认10结果，0–20；content摘要；published_date可选beta，可能为估计/更新日、也可null | 免费1000 credits/月，无需信用卡；PAYGO $0.008/credit；basic/fast/ultrafast 1credit，advanced 2 | 开发100RPM、生产1000RPM；Bearer key；[官方条款](https://www.tavily.com/terms)允许按订单集成包括AI Tools的Customer Applications；可由个人或实体签约，未发现国内主体必需；不等于源站授权 |
| [SerpAPI百度](https://serpapi.com/baidu-search-api)、[必应](https://serpapi.com/bing-search-api)、[价格](https://serpapi.com/pricing) | q与对应engine，官方例子有结果摘要；site固定查询实际效果/日期字段覆盖未测 | 免费250搜索/月、50次/小时；$25/1000（月200/小时）、$75/5000（月1000/小时）等 | 付费计划明确吞吐；[官方FAQ](https://serpapi.com/faq)Legal Shield仅称覆盖合法采集、不覆盖后续违法用途；具体AI/国内主体条款未核验；robots禁普通/search.json网页路径，不能通过未授权API调用绕过 |
| [Brave Search API](https://brave.com/search/api/) | 官方定位AI agent搜索、额外摘要与Goggles过滤；普通site语法/日期覆盖未实测 | Search $5/1000请求，月$5免费credits，50QPS；Answers $4/1000另加$5/百万输入输出，2QPS | [一般条款](https://api-dashboard.search.brave.com/documentation/resources/terms-of-service)限制持久保存、训练及benchmark；特许计划另核，国内主体要求未核验 |

博查首页示例端点api.bochaai.com与接口文档api.bocha.cn不同，本轮未验证两者等价；上线前应以当前账号正式文档为准。Feishu文档按需加载，只取到可见区，不把“目录有章节”当已读完整条款/参数。

**暂定建议**：先用已有免费账号，对博查和Tavily运行相同五查询，另以SerpAPI百度/必应作为中国语料对照；以详情URL率、岗位相关性、日期可核验率和每有效来源成本选型。Brave若作海外/英文对照，须先确认订单包含测试及存储权。当前不宣布胜出者，也不将未测字段补成支持。

### API条款补证（10-05）

[Tavily条款](https://www.tavily.com/terms)更新2026-05-04：1.2/2允许按订单将服务集成进包括AI Tools的客户应用；3.2限制向第三方披露性能分析，6.5涉及AI功能输入输出可被第三方服务商用于训练。因此内部五查询结果不能默认公开成性能榜，真实简历内容也不直接作为搜索词。

[Brave一般条款](https://api-dashboard.search.brave.com/documentation/resources/terms-of-service)更新2026-09-01：3.2限制非暂态保存及用结果评估、训练、benchmark AI模型或服务。[官网FAQ](https://brave.com/search/api/)明确存储权需计划专门授予、第三方内容权不转移。AI宣传定位不替代订单，当前不执行Brave持久留证实测。

[SerpAPI FAQ](https://serpapi.com/faq)称美国Legal Shield为Production及以上最多200万美元的合法采集保障，不覆盖用户后续侵权/违法用途；这是厂商合同说明，不是源站转载权或诉讼结论。[博查官方MCP README](https://github.com/BochaAI/bocha-search-mcp/blob/master/README.md)补证query/freshness/count（1–50）与标题/链接/摘要/发布时间输出；未找到include参数。第三方1c7镜像虽写include/exclude，本brief仅官方文档，未采纳。

## 对设计的影响

1. 第4节第5项应按小谷自有UA判断，宿主白名单不转移给服务器；第6项取消脉脉与牛客并列。
2. 第4节第3项公开引擎网页发现受robots阻断；sitemap可做ID发现/去重，却无岗位关键词，不能单独完成语义召回。搜索API需许可与质量实测。
3. 保留“从业者反馈未知”的兜底；来源字段需明确发布日期未知、截断、自填标签、岗位范围、招聘方/员工口径。招聘方指标不能换成员工绩效事实。
4. 五份JD说明算法岗包含记忆、推理部署、排序、底盘、工业控制；必须先定位子岗位。未经核验不把其它团队或全部算法岗合并。
5. 公开资料未证明竞品的员工信息检索机制；第1.3回填事实与缺口，差异仍是假设。未改运行时代码或生产采集配置。

## 验收与恢复

| 验收 | 状态 |
|---|---|
| Q1国内≥5工具、海外≥2、逐格观察 | 已交付10个；部分AI能力未验证，均明确标注 |
| Q2未登录公开DOM、SSR/HTTP、条款 | 部分；一条无Cookie原始HTTP/SSR正文已核验，条款与跨样本覆盖仍缺 |
| Q3发现质量及sitemap | sitemap1部分统计；SERP禁止、API质量未测 |
| Q4自有身份规则 | 已有逐主机证据和明确未知 |
| Q5五JD及真实员工fixture | 五JD及3帖真实fixture已保存并通过回归；四主题定性覆盖，时间百分比/同团队当前证据仍缺 |
| Q6≥4官方资料及实测 | 四候选部分官方字段；实测需凭证，条款与部分参数仍缺 |
| 设计影响 | 暂定建议，独立只读审阅PASS（部分交付） |

完整文件证据索引见tasks/research-2026-10/evidence/manifest-final.json，正文证据在evidence/live-sources-2026-10/<语义名>/cdp-page.json与screenshot.png；首轮还有URL哈希子目录的page.json/page.html。错误/跳转页仍保留但不计内容证据。目录被.gitignore忽略。恢复入口tasks/research-2026-10/start.md；历史PASS仅覆盖10-04部分报告，本次另有review-2026-10-05.md确认部分交付。

## 本轮收尾核验（2026-10-05）

独立只读审阅PASS（部分交付），Important修复已复核；见tasks/research-2026-10/review-2026-10-05.md。文件哈希清单为tasks/research-2026-10/evidence/manifest-final.json，不将错误/跳转页当正文。补效招截图的导航出现CDP_CONNECT_TIMEOUT，停止后续联网，未切路或重试；原证据保留。恢复见任务start.md，全部验收仍以正文缺口为准。

本轮web-access静态补证的原文短摘录另见evidence/live-sources-2026-10/web-access-short-excerpts.json；不把研究者复述当原始正文。新增fixture及条款补证的独立审阅另记，不沿用上一版本PASS。

本轮静态补证已获独立只读审阅PASS（增量）；见tasks/research-2026-10/review-web-access-2026-10-05.md。完整验收缺口保持，原CDP超时不影响本轮静态已取得资料。
