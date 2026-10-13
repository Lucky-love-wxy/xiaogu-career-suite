# 三份 brief 顺序调研

- 任务标识：xiaogu:research-2026-10
- 规则：/Users/lucky_wang/Documents/codex/AGENTS.md
- 原始要求：完成用户列出的 live-sources、web-agent、question-bank 三份文件要求的调研，按此顺序。
- 状态：进行中；2026-10-05（Asia/Shanghai）。最新恢复与剩余验收见文末，历史失败记录仅用于追溯。
- 验收：第一份 Q1–Q6、第二份 W1–W3、第三份真实问题原话/频次/饱和批次；各报告标事实、厂商自述、推断和缺口。
- 授权：公开只读调研、本项目报告/证据/数据写入。未授权登录态使用、购买 API、模型评测、发布或修改运行时代码。不读取密钥。
- 当前事实：项目有大量已有未提交修改；保留现有文件。AGENTS.md 项目专属文件不存在；已读取用户提供工作区规则和相关项目索引。
- 输出：docs/research/live-sources-2026-10.md、web-agent-2026-10.md、question-bank-2026-10.md；evals/question-bank/real_questions.csv。
- 下一步：先验证公开网络与 robots，再完成第一份；网络路径失败按用户规则停止联网并保存原始错误，继续无关本地准备。

## 2026-10-04 更新

- 已完成：三brief与两upstream全文、种子表头/分类、mock测试契约核对；search-test-queries.json固定查询；execution-plan.md保存逐项验收与采样规则。
- 网络：牛客robots首次curl返回exit 7，连不到127.0.0.1:7890；正文0，未更换工具/代理或重试。原始错误 evidence/network-failure.json。
- 剩余：全部公开调研、真实数据采集、API/引擎实测、截图、饱和证明、最终报告及独立审阅。没有声称三份已完成。
- 待用户答复：是否允许同curl路径正式权限复核；或由用户恢复代理后继续。

## CDP恢复

- 最新用户授权：你来发起cdp申请。正式权限申请已通过；check-deps --mode=cdp 返回proxy ready，port3456，/targets数组有效。牛客robots正文已取得：* 禁/search、/nccommon、/ab/ab-test-flow，其余不在该robots禁止范围。
- 下一步：通过任务专用标签页公开只读取证；不使用登录态；不改已有标签页。

## 最新进展与阻塞

- CDP正式获准，15页正文/DOM/截图已保存；清单 evidence/cdp-manifest.json。
- 第一份部分报告 docs/research/live-sources-2026-10.md；Q4有逐主机规则证据，Q2公开DOM可读但SSR与条款未验证，Q3仅根sitemap，其余未完成。
- 新阻塞：读取nowcoder sitemap1的CDP /eval HTTP500。证据 evidence/cdp-failure.json；根因未知，未重试或切路。
- 第二、三份尚未启动联网，真实CSV/真实JSON尚未生成，现有mock保持原样。
- 下一步：等待用户指引，获准后诊断同CDP路径，先补第一份其余验收；大页面应定向/限量读取，是否为本次根因尚未确认。

- 部分报告独立只读审阅PASS；2个Minor文案已修正，见review.md。此PASS不是三份调研验收完成。

## 最新用户修正与继续结果

- 用户更新规则后要求“继续”：CDP只能通过 node /Users/lucky_wang/.agents/skills/web-access/scripts/cdp.mjs，绝对脚本路径、单条执行、无管道、无require_escalated；旧curl/Python直连方式不再使用。
- 已执行正确格式的 targets --filter nowcoder，退出1：EPERM connect 127.0.0.1:3456。没有取得新的网页或标签页列表，也未创建标签页。
- 本地 codex execpolicy check 明确命中default.rules的prefix_rule并返回allow。不能把本次错误归因于命令写法或Chrome未开启；实际执行环境没有放行，原因未知。
- 证据：evidence/cdp-entrypoint-eperm.json。未提权、未切工具、未改规则、未联网重试。
- 原15份证据与部分报告仍有效；第一份剩余验收未完成，第二/三份未开始。
- 恢复建议：客户端/执行会话重新加载现有规则后继续同cdp.mjs入口（效果未验证）；优先验证targets，再定向读取sitemap1，避免一次返回整个大型DOM。

## 本轮恢复

- 用户继续，平台已保存cdp.mjs前缀许可；单条默认执行targets成功。
- sitemap1限量读取成功：DOM约25.8MB，不带Cookie的fetch原始XML 4,808,775字符、20,739URL、5,513/discuss/、无岗位关键词。历史500根因仍未确定。
- 只用cdp.mjs新入口，旧Python直连已停用。

## 本轮新增证据与下一步

- docs/research/live-sources-2026-10.md已更新Q1/Q3：国内3产品+海外2产品公开正文；四搜索引擎robots禁止普通SERP，不执行；sitemap1原始XML统计20,739URL、无岗位关键词。
- 页面状态证据共26份；完整索引evidence/cdp-manifest-current.json（含错误页/跳转页）；新增报告未独立review，首轮PASS仅历史部分。
- 最新阻塞：下一批首个navigate返回CDP_CONNECT_TIMEOUT，详见evidence/cdp-connect-timeout.json。剩余URL未执行；不切工具或重试。
- 已发异步问题询问Chrome授权提示，等待用户答复；根因不能仅凭提示确认为未授权。
- 任务专用标签页E720249C4DEBF9F1A7409D37CFAED01A暂保留，恢复后继续使用/最终关闭；无用户页操作。
- 原验收仍未完成：国内至少5来源、Q2原始HTTP与条款、Q5真实JD/从业者数据、Q6API比较/实测；第二/三份未开始联网。

- 本轮Q1/Q3独立只读复核PASS（部分），Minor已修正；sitemap完整XML未保存的可复算风险已记录。整体调研未完成。

## 2026-10-05 最新恢复与进展

- 用户表示Chrome已打开但没有弹窗。相同cdp.mjs入口返回有效targets，实际正文与截图再次取得；没有弹窗不构成阻塞，无需用户额外操作。
- 旧任务标签页已不存在，新建任务专用页0D3246E282A37DA1FBE31DC192A0C75B。只操作此页，不接管用户标签页。
- 第一份新增超级简历、智联、猎聘、智联求职AI公开资料；博查/Tavily/SerpAPI/Brave官方价格与接口文档；一个SKF机器学习相邻岗位JD。均保存evidence/live-sources-2026-10/<语义名>/cdp-page.json与screenshot.png。
- 未满足：搜索API五查询实际调用无凭证/计费授权；五个算法工程师JD及覆盖四主题的从业者内容不足；牛客协议原文路径被robots禁止。不以招聘列表、相邻岗位或厂商演示凑数。
- 因第一份部分验收需外部输入，已读取第二份不依赖它的官方资料：DeepSeek价格/JSON/thinking/并发，Chainlit/assistant-ui/Vercel AI SDK仓库与Chainlit面板文档。证据evidence/web-agent-2026-10。第一份仍未完成，后续报告按用户顺序交付。
- DeepSeek当前flash映射V4.1-Flash，pro映射V4-Pro-0813；峰谷价格必须分开。Chainlit仓库当前标Apache-2.0，不沿用旧MIT印象。均为官方记载，未运行服务或API评测。
- 下一步：先更新第一份报告与API缺口，再补JD/从业者来源；第二份完成资料比较后再做真实题库，不切分数据集，不消耗模型额度。新增产物尚未独立审阅。

## 2026-10-05 最终交接（部分完成；网络再次阻塞）

- 三份报告按原顺序落地：docs/research/live-sources-2026-10.md、web-agent-2026-10.md、question-bank-2026-10.md。第一份未完成时读取第二/第三独立公开资料，是执行顺序偏离，已说明；不能将文件顺序当全部验收。
- 第一份：8工具公开观察、五算法JD正文保存；单条牛客无Cookie原始HTTP/SSR正文核验，条款未知；四API官方资料部分字段，无真实调用。员工四主题样本和real fixture仍缺。
- 第二份：三开源方案许可证/结构输出/面板比较；DeepSeek官方价格、峰谷成本、JSON/thinking/并发限制。六AI实际界面、中文社区活跃度未完成，未运行服务/模型。
- 第三份：evals/question-bank/real_questions.csv共100行，92 user+8 vendor；牛客6、豆瓣86、超级简历8；表头与seed相同、split空白。覆盖57 Y/25 partial/10 N；新增求职互助4例，两批新类别1→0，仅受限样本停止数值，非完整多来源饱和。大量旧帖，最后回复≠发表日，身份未逐帖核验。
- 离线生成器evals/question-bank/build_real.py绑定每条原话和证据URL；100/100绑定、表头/空split、确定复现已验证，证据tasks/research-2026-10/evidence/question-bank-validation.json。未改seed/mock/runtime，未切评测数据，未调用付费模型/API。
- 独立只读审阅PASS（部分交付），两Important及Minor已修复；review-2026-10-05.md。历史PASS不能替代全部验收。
- 最新错误：补效招截图的导航exit1 CDP_CONNECT_TIMEOUT，20秒无调试响应。evidence/cdp-connect-timeout-2026-10-05.json。停止联网、不重试、不切工具；原因未知，不能认定Chrome未开启/用户未授权。
- 任务页0D3246E282A37DA1FBE31DC192A0C75B保留；网络阻塞后未执行关闭，未操作用户页/停止proxy。恢复后先同cdp.mjs验证相关target，再只补未完成项，结束清理自己页。
- API凭证异步问题仍待答：仅询问服务名与配置路径，未授权读密钥/扣费，不把已知key位置当批准。
- 下一步：用户恢复CDP并指引同路径继续后，先补第一份从业者四主题/真实fixture与官方缺字段；有免费API配置和明确额度范围再跑五查询。随后补六AI界面/社区统计及允许来源近期问题轮流采集。禁止用招聘JD/面试题凑从业者日常或把厂商FAQ当user。
- 没有git commit/tag/push：本任务未请求远程归档且项目存在大量先前修改。证据文件清单evidence/manifest-final.json区分保存文件与可支持结论的正文。

## 本轮web-access静态补证（2026-10-05）

- 最新用户指令：继续，并且尝试用web access解决一部分。采用skill的WebSearch/WebFetch公开静态搜索与读取；未以它替代CDP动态界面/登录态验收，原CDP连接错误仍历史阻塞。
- Q5新增3真实公开原帖fixture examples/algorithm-engineer-real/live_sources.json：两篇2024旧帖及一篇年份未知的带指导商业动机日常帖。四主题仅定性覆盖，时间百分比/绩效门槛/同公司证据/身份仍未知；相对推荐算法，感知different_team，其余unknown。保存要点来源evidence/live-sources-2026-10/web-access-supplement.json。
- 新增RealFixtureTests；首次全测发现renderer日期须YYYY-MM(-DD)，展示日期已规范，不编造未知年份；沙箱本机stub监听EPERM，正式工具批准沙箱外本地测试后70项PASS，无真实API或付费模型调用。ResourceWarning只属现有本地stub socket未关闭。测试证据evidence/tests-real-fixture.json。
- Q1/W1新增52cv职徒官网与知页公开材料；8国内+2海外，W1六工具有AI公开资料，但六实际界面仍未满足。52cv robots在静态工具不可访问，同批主页正文取得；不深入/不换路径绕过此单页失败，W1补证evidence/web-agent-2026-10/web-access-supplement.json。
- Q6补官方Tavily/Brave/SerpAPI条款/FAQ与博查MCP字段。Brave通用条款限制存储和评测用途，需要明确特殊许可；Tavily限制对外披露性能分析，API集成不转移源站版权；不是统一法律保证。候选质量仍没有实际API调用，内置工具结果不算四候选或四引擎质量测试。
- 第三份100条未改，没有宣称本轮扩大/刷新/全来源饱和。本轮增量独立只读审阅PASS，见review-web-access-2026-10-05.md。
- 当前恢复顺序：第一份API质量需具体配置/免费额度范围及适用条款；Q5工时占比与当前同岗位可靠证据仍待补；之后第二份实际界面/中文社区、第三份近期多来源。用户新指令允许web-access静态路径，后续可继续此路径的未完成公开资料；无需反复要求重开Chrome才能做静态研究。

- 本轮最后更新时间：2026-10-05T13:01:43.464421+08:00。静态路径已取得实质结果，无新增全局传输失败；52cv robots单页读取失败保留为规则未知，不深入交互。完整任务仍进行中，缺口不变；无需把Chrome弹窗当静态调研门禁。

## 医学专业实际去向新任务（2026-10-05，用户已明确开始）

- 原始目标/验收：notes/2026-10-05-codex-research-brief-major-destinations.md，Q1至少10校三档各3及4省、Q2职业族、Q3每岗位3不同公司JD与搜索词/条数、Q4编辑细分、Q5五产品；三个CSV、离线复现、报告。上游notes/2026-10-05-direction-guidance-redesign.md。不得改runtime/prompt/tests/fixture，不模型调用/注册/付款/发送。
- 最新用户修正：自行调取BOSS URL，获取中大厂详细JD。按医学非临床方向执行，规模至少500人作为候选筛选定义，待核招聘方原文；不是正式企业分档。
- 已读brief/upstream与项目索引、安全策略；project AGENTS不存在。技能research-collection/web-access/PDF已加载。旧三brief任务未被本次开始视为完成。
- 当前：找到5公司BOSS聚合页线索，evidence/major-destinations-2026-10/boss-candidate-urls.csv；这些不是单职位详情URL，不填role_postings、不累计JD门槛计数。搜索缓存可能旧，城市/规模/时效未独立验证。
- 阻塞：本轮WebFetch读取https://www.zhipin.com/robots.txt返回Internal Error无正文。保存boss-access-status.json；按最新用户联网规则停止，不切路重试。历史robots仅2026-10-04记录，不能作本轮新验证。
- 本机boss已安装（command是boss，不是boss-agent-cli）；源码detail HTTP失败自动降级browser，Patchright/Playwright会违背禁用规则，未执行、未读账号凭证。禁止为成功绕过网络错误或自动换CLI。
- 下一步：待用户对失败路径给恢复指引；可指定已授权cdp.mjs重核BOSS规则并仅浏览允许的公开聚合/详情路径。之后提取真实详情URL及正文，若登录/安全页即保持未验证。学校Q1尚未采集，三个最终CSV未生成。证据目录git check-ignore已确认忽略。

## 医学去向：BOSS登录会话恢复与6完整JD（2026-10-05）

- 最新用户授权：已登录BOSS直聘，让我获取；覆盖本次BOSS登录会话只读，不投递/消息/注册/凭证导出。其他来源/付费授权不扩大。
- cdp.mjs targets成功，新建任务页EE63B12140B05A0604E6C1E3586A4D54；保留原用户页1CCB8DD93D1BFAC2B79EB9A4E92041A0。robots新正文取得，读取无参数/非l开头详情；公开SEO路径发现链接，未执行含query搜索。
- helper一条未加引号的URL导航EPERM；按规则修为url='完整URL'后同入口成功，无提权/换工具。其余正常。登录页用户名只曾在工具正文出现，不进入保存证据；后续定向JD/公司字段，HTML仅职位节点。
- 完整JD六份六公司：医学编辑=阿里健康、澳鹏、万声；CRC=泰格思默、津石、诺思格。平台规模均≥500，未独立核企业人数；医院场景CRC不等于非医院。
- 报告docs/research/major-destinations-2026-10.md（部分验收）；data/directions/major_destinations.csv仅表头，role_postings.csv6条，role_summary.csv2条；scripts/build_major_directions.py离线生成/计数/哈希。
- 经验不限不等于无实习可录用：澳鹏优先临床见实习；万声必需执业医师证；阿里5–10年；泰格CET4；津石27届实习；诺思格正文半年CRC/卡片1–3年。计数口径和门槛冲突已披露。
- 验证6/6原文绑定、3公司/角色、计数复算、确定复现PASS；证据evidence/major-destinations-2026-10/validation.json。待独立只读复核本批；不调用模型/CLI，不改小谷runtime/tests/fixture。
- Q1学校PDF0；Q2大典无原文/编码空；Q3搜索计数robots受限；Q4三内容职责簇各1份；Q5复用5相邻产品公开功能不是实际方向工作台。整brief未完成，不据6JD声称“毕业生实际去向”或主推3+次选2–3数据足够。
- 本批下一步：完成只读审阅、清理自己新建tab、保存日志；较大任务后续先补10学校/三档/四省与大典，再扩角色。既有三份brief仍保持原完成边界。

- BOSS本批只读审阅PASS（部分交付），见review-major-boss-2026-10-05.md；津石在读资格文案差异已补。新建页EE63B12140B05A0604E6C1E3586A4D54 close success，用户原页未操作。最后更新时间2026-10-05T13:55:30.250156+08:00。


## 医学去向：学校数据与公众号/学生平台补证（2026-10-05T14:14:35.396028+08:00）

- 最新用户修正：询问未完成项能否通过公众号、知乎等学生平台解决；继续补证，不把前一批JD当整体完成。
- 已完成：康达学院2024届官方HTML年报和目录核验（C档江苏，2025-11-25发布，目录未列2025届）。定向DOM原表 evidence/major-destinations-2026-10/school-kangda/source.json。
- CSV109行=89数值+20缺失；5目标专业有专业级去向结构/单位性质/行业/职业类别；中医、医学影像学、口腔未按该专业列出，不把医学影像技术改名。企业比例分母是已就业者，不能推出全体转行比例或具体CRC/编辑岗位比例。网页表号不冒充PDF页码，PDF0，10校/三档/四省验收未通过。
- scripts/build_major_directions.py已支持从固定DOM表离线重建；89/89绑定、五专业去向结构原值合计、109行与确定复现PASS，school-validation.json。六JD/两岗位CSV哈希未改变。
- 替代入口：教育部学生服务与素质发展中心报告汇总有官网与公众号链接；广西医大年报确认2025就业质量报告存在及微信公众号渠道，未取得报告内数据。牛客一篇生物学/生信转数据个人自述已读，有推广，非临床专业，不进学校CSV；知乎旧讨论仅发现线索，未核正文。详见alternative-entrypoints.json和主报告Q1。
- 真实阻塞：两官方大典PDF405/Internal Error；微信robots无法打开、知乎robots超时；天津医大PDF、天津医学高专2025发布页、承德2024报告页超时，长春中医药链接过期；温医仁济发布页有正文但报告图片失败；近期牛客feed Cache miss。失败URL未切工具重试；按用户AGENTS等待下一步指引。
- 已发异步问题：失败静态入口是否允许改用已有Chrome CDP只读核验。已有CDP授权仍有效，问题针对用户规定的失败路径切换，不要求重新登录授权。未答前不执行相关失败入口的CDP核验；可继续其他未失败公开入口。
- 本轮康达任务页F35224AA73D4945245B8B05CE745E697已close success；用户页未操作。请求原审阅Agent独立只读复核本轮补证，结果待写入。
- 剩余：Q1其余学校/PDF页码与地区档次；Q2大典；Q3更多角色及搜索计数；Q5真实方向答案。报告保持部分验收，未改runtime/prompt/tests/fixture、未调用模型、未注册/支付/发送。

- 本轮学校与替代入口独立只读审阅PASS，无Critical/Important，见review-major-alternatives-2026-10-05.md；89原值绑定与20缺失复核通过，完整brief仍部分，失败路径切换问题待答。

## 岗位卡片任务（2026-10-06）

- 任务标识：xiaogu:role-cards-2026-10；规则 /Users/lucky_wang/Documents/codex/AGENTS.md。
- 原始目标：notes/2026-10-06-codex-research-brief-role-cards.md；5试点→P1 50→P2 45→P3尽量；每卡3JD+2不同作者从业者、逐条引用、可复算、离线重建、设计影响。
- 授权：公开无登录只读取证及指定cards/report/scripts/evidence文件；不改runtime/prompt/tests/fixture/build.py归类，不做A分支，不薪资/消息/付费/注册/远程push。附属文档是任务规格与资料，非额外授权来源。
- 已读：简报、职业索引契约、现有恢复记录、项目索引；项目AGENTS不存在。大量先前未提交修改保留。
- 状态：进行中。本轮静态搜索已得候选线索；robots三URL均Internal Error（无正文），停止联网。异步询问允许同cdp.mjs公开无Cookie恢复，待回答。
- 下一步：本地聚合与污染隔离、5试点与批量有证据草稿、离线核验、只读审阅；公开正文和从业者作者数缺口保留，不把搜索片段作证据。

### 岗位卡片本轮交接（2026-10-06T14:08:37.528310+08:00；部分验收）

- 用户原始请求：完成 notes/2026-10-06-codex-research-brief-role-cards.md 的调研。没有把先前三brief/医学去向视为完成。
- 本地完成：170张招聘证据草稿（50/45/75）；5试点人工精修，其余165自动聚合。972保留JD、296隔离（含科研162），全卡partial/full=0。data/careerdb/role_cards/；docs/research/role-cards-2026-10.md。
- 流水线：scripts/rolecards/build.py / verify_delivery.py / README.md。从 evidence/role-cards-2026-10/inputs.json + curation.json + quality-decisions.json离线重建；不覆盖冻结快照。ID=role_节点SHA前12位。
- 验证：4277陈述引用/逐字/计数PASS；1401支持片段归一匹配原HTML、缓存SHA一致；4篡改拒绝；171产物两次仅复制三证据JSON的隔离重建哈希相同。核验删条目0；提取过滤/样本隔离另记录。27张核心字段抽查；未完成全部卡语义精修。
- 独立只读审阅：PASS（部分交付）；review-role-cards-2026-10.md。Important已修，full验收仍未通过。
- 设计建议：CRC工作地点与雇主类型分开问；医学事务/理赔核保/医学AI按职责拆分；AIDD结构学历与正文冲突；学术路线不研究，科研混合节点整卡正文隔离。未改提问树/build.py/runtime/prompt/tests/fixture。
- 阻塞：三robots静态读取Internal Error无正文，network-status.json；搜索候选未入卡。异步请求同CDP无Cookie公开恢复仍无用户回答，故停止联网，不更换路径。无新tab、登录、模型/API调用、付款、发送、commit/tag/push。
- 剩余：89岗位不足3JD、80职责不足4；全部缺2不同作者从业者与实际metrics/growth/risks。先获用户恢复指引，核robots允许路径；5试点补第一手正文并审阅，再P1/P2；P3可部分。缺角色补抓不翻页、牛企间隔4秒、其他站3秒；不用登录态。
- 恢复入口：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/tasks/research-2026-10/start.md；证据目录受既有gitignore保护，必须保留本地目录。

### 用户修正：脉脉/牛客与CDP（2026-10-06）

- 用户明确：从业者参考脉脉和牛客；允许使用CDP。覆盖brief禁脉脉及先前失败后切换路径等待；不扩大到登录态/付费/发消息。
- cdp.mjs targets有效；任务专用robots标签CA2F29C739A4FEF936BC18782BD482F3（脉脉）、093329D35BD34D55854D23225E25A4F4（牛客）。用户页未操作。
- 两站robots正文新取得。脉脉明确允许OpenAI user-triggered fetcher公开article/detail等，默认其他路径禁止；牛客禁止/search、/nccommon、/ab/ab-test-flow。只用允许公开路径，不站内搜索禁止路径。
- 下一步：站外发现候选，CDP fetch credentials omit取公开正文；推广/求职提问不当从业者。先5试点再P1/P2，卡片整体验收状态未改变。

### 最新授权与API准备（2026-10-06）

- 用户明确牛客、脉脉均已登录，允许相应只读会话；TikHub提供已登录API后台URL。现有Key仅在内存使用，不显示、导出或持久化，不创建新Key/增权/充值。
- 用户明确允许脉脉超时后改同入口逐页并继续；TikHub现有余额最多US$0.10且最多30成功请求。官方小红书单价US$0.01，本批更严最多10总请求（失败也计保守上限），无自动重试。
- TikHub后台余额9.67美元、显示免费额度0.05美元；不是已调用或扣费证明。API官方app_v2/search_notes与get_image_note_detail已核文档，旧MCP未暴露在本会话。
- 脉脉6页一次Runtime.evaluate超时无批次结果，未计正文；研究tab多次消失，原因未知。既有用户tab未导航；牛客仅同源公开fetch credentials omit取得CT物理算法原文及日期，作者hionling，内推商业动机保留，不能当整个医学AI职种证据。

### 岗位卡片：本人分享补证交接（2026-10-06T14:47:45.191334+08:00；部分验收）

- 最新用户修正/授权：牛客、脉脉已登录并允许只读；脉脉超时后允许同CDP逐页恢复；小红书经TikHub现有余额最多US$0.10/30成功请求、不充值。官方单价0.01，因此实际按10总请求硬限执行，已耗尽。此前不付费/禁脉脉由当前明确授权覆盖。
- 完成：7本人来源（牛客CT算法1，小红书CRC2/PV2/MSL2）入卡19新陈述；脉脉4正文属推广/岗位介绍/历史二手/JD合集，不计本人。小红书仅文字，未审图；核保搜索仅候选。
- 卡片170张（50/45/75），CRC与PV两张full，MSL/CT子类证据整卡仍partial；full仅数量及适用门槛，不保证实名认证/代表性/所有字段完整。972可用JD；4296陈述引用绑定PASS。仍167岗位不足2作者，89不足3JD，79职责不足4。
- 验证：1401原HTML支持片段、4篡改拒绝；11输入（4输入JSON+7正文JSON）两次隔离重建171产物哈希一致。review-role-practitioners-2026-10.md最终PASS（部分），Minor表格竖线已修并复核。
- 费用：10成功=4搜索+6详情，余额9.67→9.57，US$0.10；免费0.05未变，滞后日统计8/.08未作为额外额度。无充值/新Key/增权；Key只在任务浏览器内存使用后删除，未保存。tikhub/manifest.json与billing.json可复核。
- 清理：本批TikHub任务页F0DD8462A84524A28D47E9D279372BD1已close success；用户牛客/脉脉/TikHub原页未导航或关闭。研究robots页先前消失原因未知，未接管用户页。
- 输出：docs/research/role-cards-2026-10.md、data/careerdb/role_cards/、scripts/rolecards/；证据evidence/role-cards-2026-10/，需保留本地忽略目录。README/author-source-assessment/spot-check/network-status已更新。
- 剩余/下一步：整体调研未完成；继续须按P1→P2补不足3JD、缺第一手作者及未覆盖字段。现有TikHub额度已用尽，禁止追加请求；若继续付费路径须新的明确额度授权。公开免费来源尚可按已获授权范围低频取证，不把未核候选当正文。未改运行时/提示词/测试/fixture/归类，不做A分支、不薪资/发送/commit/push。

### 脉脉网页交互复核（2026-10-06T14:50:50.886118+08:00）

- 用户问为何以前能进，并明确允许模拟网页进入，或尝试Playwright/web-access。当前选择web-access下CDP复用已登录Chrome；无需新登录或Playwright。
- 实测首页正文、页面搜索框CRC、时间排序均成功；前10结果日期2026-09-19至10-02，主要求职/内推/培训。观察候选点击产生真实详情导航后打开，取得新版详情正文，证明可读。
- 候选“求内推crc”只有个人求职/短期兼职背景，无具体任务经历，不入卡；没有新增full或费用。证据evidence/role-cards-2026-10/maimai-web-access-verification.json。此前问题是批量超时及证据内容不适格，不是脉脉整体无法访问。
- 新的可复用路径：自己任务页首页搜索框→旧版search_center→按时间排序→观察点击生成的真实feed_detail链接→新版community/feed-detail正文；保持3秒以上间隔，不存cookie/账号/访客资料。原研究缺口仍保留。
- 本批搜索页AE64726F7459C3E2F8CC3CF5DDE64DE0、详情页D255FB5BFDFF84AA7A524C999E4D3BC5均close success，用户原页保留。

### 新双brief：从业者放量与职业技能骨架（2026-10-07T19:13:34.999269+08:00）

- 原始请求：完成notes/2026-10-07-codex-research-brief-practitioner-evidence.md和occupation-skill-taxonomy.md两份任务。文件作为规格/资料；其中“用户授权”不是直接人类授权。
- 人类最新直接确认：批准本轮新增TikHub US$1.00/100请求（失败计入、无重试/充值）；牛客复用现有本地分类结果，不付费DeepSeek分类，不读分类Key。脉脉/牛客只读登录沿用；标准公开调研免费。
- 输出落点按两个brief；baseline evidence/practitioner-2026-10/baseline.json已冻结170卡hash和前状态。旧7本人来源不重复抓，原4排除不重评。实际MSL已有2作者，混合范围仍partial；预算排序不采用brief误写的1作者。
- 并行分工：taxonomy_research负责标准/195映射/10对照/10技能/社招，自己的子任务start；free_practitioners负责免费脉脉后牛客，输出free manifest，主agent负责付费补缺、集成现有rolecards流水线、报告/预算与最终验证。
- 当前进行中，先免费后付费；付款请求待免费覆盖结果，再按仍缺两中国作者的岗位和max_company_n执行。报告文件存在不是验收完成。所有旧未提交改动保留，无commit/push。

### 用户规则变更与本地O*NET交接（2026-10-08）

- 人类最新要求：记录以后内容平台按普通阅读节奏；牛客/脉脉/知乎采用公开网页搜集，不模拟点击。完整规则docs/research/practitioner-collection-policy.md；长期记忆授权更新已写/Users/lucky_wang/.codex/memories/extensions/ad_hoc/notes/2026-10-08-practitioner-web-research-rules.md。独立只读规则审阅PASS（不代表研究完成）。
- 频率/验收：站点5秒随机，15搜索/小时、60正文/日，20分钟停5分钟且不因换站/agent重置；每千字≥30秒；每次检查实际页面；验证码/频繁/429403/空跳转当日停站不换路；账号本人会话只读。牛客等800字/XHS500字+本人timeline/scene，短文不打开，系列作者1名；渠道增加正文字数。新增丁香园/蒲公英/药智/知乎长回答，后续核具体路径再访问。
- 最新付费事实：tikhub request001未知页消失未重试，002–023共22成功，保守计23尝试；余额9.57→9.35，实际US$0.22，免费0.05未变。剩余最多77尝试/保守US$0.77，不充值。Key已删除、任务页A7BEEA36ED800BBA18441FCE8CAB4944已close success。billing.json/manifest.json已更新，不能继续使用旧浏览器target或内存Key。
- 本轮增量实际卡仅已集成免费算法252字源5陈述（4301陈述）；TikHub多篇curated仍未集成，勿把curated文件当入卡完成。word-count-audit.json审查16现存正文，多数不满足新门槛；字数达标仍须本人/岗位适用审阅。保留旧短证据，不能冒充新长文验收；channels.csv已新增正文字数但付费渠道完整汇总尚待集成，报告整体未最终验收。
- 用户下载提供 /Users/lucky_wang/Downloads/浏览器/db_31_0_excel/，只读ReadMe确认31.0 August2026 CCBY4，5表行数/SHA核验 evidence/taxonomy-2026-10/user-excel-verification.json；不重复下载该包、不修改Downloads。此前CSV包与ESCO包已在taxonomy evidence中，子任务start保存该任务详情。
- 剩余：按新方法/门槛完成长文样本采集、量与渠道产出验收、脚本实际限频/停站检查；taxonomy195映射/10任务/10ESCO技能已局部生成但标准大典/ISCO/社招失败缺口与独立审阅尚未核清。历史4robots和ISCO恢复问题尚无明确答复，下载ZIP只解决O*NET，不作其他恢复授权。

### 最新AGENTS网络规则覆盖（2026-10-08）

- 用户提供整份新AGENTS替换旧AGENTS：取证脚本→静态→CDP→CU；普通目标正文实证失败自动升级，不再等待恢复指引；环境/写法错误先诊断，权限拒绝/审批不足/验证码/需要登录停止，不Playwright。
- 内容平台的直接特殊要求优先：牛牛/脉脉/知乎网页搜集不模拟点击，长文、节奏、当天停站等仍保持，不能用自动升级绕过配额墙/403/429。此前关于4招聘站robots/ISCO官方取数失败的恢复等待由新规则解除，taxonomy agent已获通知继续同源CDP取证，原失败保留。
- 用户Downloads本地O*NET已核五表行数与原CSV一致，不重复下载；不是其他平台/付款授权。两份原调研仍进行中。

### 2026-10-08 本轮部分交付（2026-10-08T10:35:43.195106+08:00）

- 原始目标仍为两份10-07简报；用户“继续”不是只整理文件。当前部分交付，未达到全部验收。以两个evidence目录execution-status.json为最终实情，历史段落不覆盖本段。
- 新增12本人来源+1O*NET生信2任务源，170卡4328陈述。原JD字段不变；历史P1 full2→5；当前长文P1 full0，新来源长文2/12=16.7%，旧短文逐篇理由列在报告。25输入/171输出隔离两次哈希一致；1401缓存支持片段/4篡改与4证据契约否例PASS。
- 报告及渠道表：docs/research/practitioner-evidence-2026-10.md及-channels.csv，字数逐篇绑定正文。实际TikHub23尝试/22成功/1未知，余额9.57→9.35扣费.22，剩77尝试/保守.77；Key清除不再付费探未知字数。
- 新阅读guard14否例PASS，但真实操作仍失败：本轮reserve休息拒绝后同一functions编排误发1牛客静态查询，UnexpectedStatusCode无正文，保存free/longform-static-error-002与ledger。保守当天停牛客；脉脉历史限额后10请求仍记录，未确认恢复。跨日不自动解锁，恢复仅原受限入口。后续网络调用必须在reserve成功的明确条件分支内执行，不能无条件串后续工具。
- 新产品长文1173字，带付费工具推广，实际阅读完成；保留动机，仅采任务，无工具求职因果/薪资/效果数字。第二产品候选未取到正文。行业社区6搜索逐词/候选数缺保存，三岗/规则/知乎未完成，不报真实零检出。
- 标准产物：docs/research/occupation-skill-taxonomy-2026-10.md与-sources.csv；data/careerdb/node_mapping_standards.csv195候选（92broader/55narrower/48none，最终认可0）、onet_transfer_check.csv100任务54动作检出、esco_skill_pilot.csv529关系395 URI。字段/计数自检PASS。
- 本地用户O*NET Excel31.0五表核行数/SHA，未逐字段等价；不再下载O*NET。广元大典PDF静态405后CDP200/29MB下载，但78页首为附件7岗位类别编码表，版本未证实，隔离raw/dadian-candidate-appendix.pdf，未写大典编码。正式全文/许可、195语义最终映射、四社招规则与两档样本/O*NET方法原URL仍缺。
- 独立综合审阅已产物质量PASS/整体验收NEEDS_CHANGES，docs/research/review-research-2026-10-08.md；不作完整成功宣称。taxonomy/free并行进程受到会话额度中断，主进程完成上述整理，未付费分类。
- 下一步：先从taxonomy正式标准/许可与195节点逐项语义审阅继续，不再把候选当验收；内容站按实际恢复状态与长文门槛补缺。保留全部已有修改，无commit/push、无运行时/提示词/fixture/职业树变更。

- 本轮新建标准PDF页3CEE53897BF14A4FF68E1A29251C135F与已完成长文任务页4B3E680323FDECDB4C64B03994F5078B均已close success，未关闭用户页面。taxonomy原长期任务页保留以待后续，继续前核实际target。

## 中国官方职业体系补充调研（2026-10-08）
用户新要求的体系设计及复用判断已交付，详见 china-occupation-system/start.md 和 docs/research/china-occupation-system-2026-10.md。建议中国标准定本土边界/能力、ESCO补技能关系，未改职业树；195中国认可映射仍0，原简报剩余保留。完整规程及动态门户正文未取得，CDP连接超时，未擅自重启或切换绕过。
