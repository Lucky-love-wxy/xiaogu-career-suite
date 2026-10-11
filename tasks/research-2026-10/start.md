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
