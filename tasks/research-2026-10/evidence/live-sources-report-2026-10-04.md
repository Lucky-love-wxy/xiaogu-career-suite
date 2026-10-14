# 岗位理解实时来源调研（部分取证，尚未完成）

访问日期：2026-10-04，Asia/Shanghai。任务：用户要求按 live-sources → web-agent → question-bank 三份 brief 顺序完成。本文只报告第一份已取得的证据；不把暂停当作验收通过。

## 当前结论

已正式获得 Chrome CDP 权限，现有代理 `/targets` 数组有效；首轮取得15个URL的页面状态、DOM HTML及截图（含robots错误页与跳转页）；本轮新增证据见文末。牛客讨论详情可以在显示“登录 / 注册”的状态读取；面经详情样本有付费截断。牛客主站 robots 没禁止讨论详情，但注册协议所在静态域名全站禁止。**robots放行不等于条款允许自动抓取或商业复用；本轮不能据此批准生产采集。**

历史上读取sitemap1的`/eval`曾返回HTTP500，本轮已通过限量读取恢复，取得其原始HTTP统计。最新阻塞是下一批导航的`CDP_CONNECT_TIMEOUT`，不是此前500或EPERM；本轮已暂停联网等待用户提供Chrome授权提示情况。根因未知，不断言网站不可用或确有授权弹窗。第二、三份尚未开始联网采集。

## Q1 同类产品信息来源（本轮新增五个产品公开正文）

访问日期均为2026-10-04；本轮只有国内3个、海外2个产品正文，国内至少5个的要求尚未达到。页面没有展示某能力时记“未找到”，不能推出产品绝对没有。厂商页面展示的效果与数据来源自述尚未独立验证。

| 产品 | 岗位实际做什么的信息来源 | 来源与日期 | 招聘方/员工区分 | 公开失败/降级 | 本次证据 |
|---|---|---|---|---|---|
| 效招Joblytic | 岗位看板展示JD信号、个人经历匹配与“问招招”示例；第三方从业者内容或模型常识来源未披露 | 样例未展示引用链接、岗位发帖日或分析日 | 未找到员工反馈分层；呈现招聘要求和候选人能力信号 | 只验证公开示例；真实追问与登录后失败表现未测试 | [岗位看板](https://xzjobs.cn/products/job-board)，本次DOM；样例不证明真实岗位数据 |
| 牛客AI功能 | 入口展示按公司/岗位划分的模拟题、面试押题、专项练习；同站有用户面经，但AI答案是否使用这些UGC未披露 | 真题标题含年份和公司，推荐面经显示时间；AI答复逐条来源未找到 | 题目分类不能替代招聘方与员工说法区分，未找到 | 页面显示登录/注册；未启动面试、未核验实际降级；另有付费面经截断样本 | [AI面试入口](https://www.nowcoder.com/interview/ai/index)和Q2详情 |
| BOSS直聘（AI待进一步核验） | 公开主页展示招聘职位、公司规模/融资等；内置AI如何生成岗位理解未找到 | 卡片展示公司/职位；本页没有足以核验AI溯源的答案与日期 | 员工反馈区分未找到 | 请求首页跳到城市页，公开列表可见；AI入口/答案未测试 | [公开主页](https://www.zhipin.com/)，实际跳转城市页；不把招聘列表当AI功能证据 |
| Teal | 厂商称可从40多个招聘网站收藏职位，以JD关键词匹配简历、管理求职；员工日常UGC来源未找到 | 职位来源通过收藏的招聘网站概念体现，首页未展示答案级来源日期 | 员工口径区分未找到 | 首页只到注册/登录引导，未体验登录后故障与降级 | [Teal首页](https://www.tealhq.com/)；“6倍面试”等是厂商效果自述 |
| Jobscan | 厂商说明上传简历、粘贴JD，分析技能/关键词与匹配；不是员工反馈验证 | 所输入JD为材料来源；首页未展示外部引用日期 | 招聘文本与员工UGC区分未找到 | 首页导向注册/扫描；未体验真实扫描或故障降级 | [Jobscan首页](https://www.jobscan.co/)；ATS逆向与回访提升为厂商自述 |

候选但未完成的来源：超级简历已读取[robots](https://www.wondercv.com/robots.txt)（`*`禁`/en/`、`/cvs/`），产品正文尚未执行；多面鹅候选`www.duomiane.com`的robots请求返回`ERR_CONNECTION_CLOSED`，域名归属尚未确认，不重试或作为官网已验证证据；职徒候选域名归属未确认。看准当前公开入口为婚恋产品，不能用它凑国内求职产品数量。Glassdoor仅有robots证据，产品正文未读。

初步推断：已经核验的公开交互主要把招聘文本或题库转为匹配/练习，未证明“员工日常岗位口径”是默认可溯源步骤；这只能说明公开证据缺口，不能证明小谷已建立市场差异。

## Q2 牛客可访问性与条款

| 样本 | 本次观察 | 日期与标签 | 边界 |
|---|---|---|---|
| [讨论：暑期实习刷题程度](https://www.nowcoder.com/feed/main/detail/085f500846374269af6c3b75b9d0b9ac) | 显示“登录 / 注册”；标题、两句正文及3条评论可读，浏览145、评论3 | 发布显示“昨天22:56、已编辑”，自填“Java”标签；没有在职/实习认证证明 | 浏览器DOM取证，未做curl或不带Cookie的原始HTTP验证；不能证明SSR |
| [面经：超聚变嵌入式二面](https://www.nowcoder.com/discuss/934495940616998912?sourceSSR=home) | 显示“登录 / 注册”；DOM中公开题目及答题建议可读，截图时有注册登录遮罩，不能等同用户无阻碍浏览；页面明确“剩余60%内容，订阅专栏后可继续查看/也可单篇购买” | 显示09-29 17:13、自填嵌入式软件开发；不是在职认证 | 不是算法岗从业者日常样本，不能充Q5；未验证原始HTTP HTML |

以上可证明公开DOM可读和面经并非统一全量可读，不证明小谷自建HTTP请求有相同能力。保存的 `page.html` 是浏览器执行后的DOM，**不是curl原始响应**。

首页给出的条款原文链接：[注册协议](https://static.nowcoder.com/protocol/register.html)、[隐私政策](https://static.nowcoder.com/protocol/privacy-policy.html)。已先核验[静态域名robots](https://static.nowcoder.com/robots.txt)：`User-agent: *`、`Disallow: /`。遵守brief的禁止路径不访问要求，未取这两份条款正文。自动化访问、AI抓取、转载引用的原文条款均**无法确定**；不能用主站robots代替协议许可。可由网站提供允许获取的条款文本或授权接口后核验。

## Q3 发现路径（robots边界与sitemap实测）

先核验四引擎robots，按未列名代理的`*`规则，普通搜索结果页均被禁止。因此没有执行两条固定查询，也没有可排名的中文搜索质量结果。不冒用白名单UA，不把“未执行”写成“搜索返回0条”。

| 引擎 | 本次规则 | 两固定查询 | 条数/前十详情率/新近度 |
|---|---|---|---|
| [百度](https://www.baidu.com/robots.txt) | `*`全站Disallow | skipped_robots | 未测 |
| [必应](https://www.bing.com/robots.txt) | `*`禁`/search`、`/Search` | skipped_robots | 未测 |
| [搜狗](https://www.sogou.com/robots.txt) | robots完整正文9955字符，末尾`*`全站Disallow | skipped_robots | 未测 |
| [Google](https://www.google.com/robots.txt) | `*`禁`/search`，普通文本查询不属允许例外 | skipped_robots | 未测 |

公开SERP网页抓取不是本次约束下可用发现通道。**暂不推荐四者之一**；应转向具有许可的搜索API，但API质量要独立测（Q6仍待凭证/额度确认）。

[牛客根sitemap](https://www.nowcoder.com/sitemap.xml)列出`sitemap1.xml`和`sitemap2.xml`，显示`lastmod=2026-10-04T01:00:03.342+08:00`。根文件使用urlset而非sitemapindex。

本轮[sitemap1](https://www.nowcoder.com/sitemap1.xml)读取成功：浏览器DOM约25,806,738字符；通过CDP内`fetch(...,{credentials:"omit"})`取得HTTP200原始XML，共4,808,775字符、20,739个URL，其中5,513个包含`/discuss/`。全部20,739条声明`changefreq=daily`，样本末尾包括`/feed/main/detail/`。文件中的“算法/推荐/面经”匹配数为0。证据 `tasks/research-2026-10/evidence/sitemap1-summary.json`。

限制：daily是文件声明，单次观察不证明实际每天更新；`lastmod`不能代替帖子的首次发布日期。仅测一个子文件，不据此推算全站体量。ID链接没有标题/岗位关键词，因此适合作新增发现/去重输入，不能直接替代岗位语义搜索。先前HTTP500不能证明该文件不可访问，限量读取已成功；大体积DOM可能相关，但根因未完全确定。sitemap2尚未测。

脉脉按最新Q4对小谷自有UA禁用；未访问其内容或sitemap。

## Q4 自建 XiaoguBot 的候选规则

以下按未列名UA适用的 `*` 规则解读；用浏览器读取规则并不证明实际发出了XiaoguBot UA。没有冒用白名单身份。

| 来源/主机 | 本次robots正文 | 详情路径判断 | 商用采集判断 |
|---|---|---|---|
| [牛客www.nowcoder.com](https://www.nowcoder.com/robots.txt) | `*`禁`/search`、`/nccommon`、`/ab/ab-test-flow` | `/discuss/`和`/feed/main/detail/`未被该规则禁止；观察到了两种详情 | 条款未能获取，未批准 |
| [static.nowcoder.com](https://static.nowcoder.com/robots.txt) | `*`禁`/` | 全站禁止，包括注册协议路径 | 不访问禁止路径 |
| [看准www.kanzhun.com](https://www.kanzhun.com/robots.txt) | 请求跳到婚恋主页，未返回有效robots规则 | 无法确定；求职详情入口未确认 | 不启用 |
| [知乎专栏zhuanlan.zhihu.com](https://zhuanlan.zhihu.com/robots.txt) | `*`允许`/tardis/jm`、禁止`/` | 普通`/p/`不在允许路径内；不抓 | 不启用普通专栏 |
| [应届生www.yingjiesheng.com](https://www.yingjiesheng.com/robots.txt) | `*`禁`/cache/`、`/datatemp/`、`/includes/`、`/toolkit/`、`/attachments/`、`/maintenance`、`/emailfriend.php` | 其他路径未被此robots禁止；尚未实测招聘详情或条款 | 待核验；不能把主站规则沿用到BBS子域名 |
| 脉脉 | 本次brief已给出`*`全站Disallow，按要求无需再测 | 小谷不可用来源 | 排除；不是本次新实测 |

## Q5 真实算法工程师数据

未取得五份真实JD或符合要求的算法岗从业者帖子。当前读取的刷题问题与嵌入式面经不满足日常占比/加班/指标/成长要求，因此未灌入真实数据集。`examples/algorithm-engineer-mock/live_sources.json`保持模拟属性。

本地契约核对：`tests/test_live_sources.py` 的 `test_mock_posts_cannot_pass_as_real` 明确要求当前mock文件所有帖子 `mock=true` 且URL为 `mock://`。将真实资料直接覆盖该文件会违反现有验收。后续真实JSON需独立保存、沿用字段，并增加或接入对应真实fixture验证；原mock测试通过不能证明真实fixture可读。未运行模型评测。

## Q6 搜索API

尚未读取官方文档或调用API，博查、百度千帆AI搜索、Tavily、SerpAPI均不能作已完成比较。固定五查询预注册在 `tasks/research-2026-10/search-test-queries.json`。各候选价格、免费额度、限流、site支持、摘要/日期、商用条款和国内主体要求均待核验；中文结果质量必须实测API，不能用浏览器搜索冒充。凭证与付费授权尚未核对，不读取密钥或调用扣费接口。

## 对设计的影响（暂定建议，不是已实施变更）

1. 上游第4节第5项的判断对象应改为**小谷自己的UA/主机/具体路径**，不再依赖WorkBuddy或Codex宿主身份。第6项脉脉与牛客并列已被本次brief最新限制否定：自建小谷排除脉脉。
2. “从业者反馈未知”的兜底仍必要。牛客样本证明有付费截断与自填标签，公开可读不能等同完整、可信的员工反馈；记录公开范围和身份证据等级。
3. 上游1.2“知乎不可用”应精确为普通详情禁止、存在`/tardis/jm`例外；该例外不意味着可以改写或绕到被禁详情。
4. 看准旧定位需移出已确认候选；请求跳主页不是robots放行。应届生按主机单独核验，不能把www规则套到BBS。
5. 尚无证据说明竞品如何读取从业者信息，不回填1.3为已完成；不凭旧报告推出差异已成立。不改运行时代码或生产抓取配置。

## 证据、失败与验收

首轮15份文件位于`evidence/live-sources-2026-10/<URL-SHA256前12位>/`：page.json、body.txt、page.html（执行后DOM）、screenshot.png；历史清单cdp-manifest.json。本轮11份位于同目录的语义命名子目录，保存cdp-page.json（请求URL、实际URL、正文、链接、访问日）及截图；效招未取得截图。本轮不再返回完整HTML。累计26份页面状态/25截图，当前清单`tasks/research-2026-10/evidence/cdp-manifest-current.json`。sitemap1保存原始HTTP返回的统计summary，未保存完整XML，因此独立审阅不能复算20,739等计数；这是剩余证据风险。证据目录已被.gitignore忽略。

- 首次curl exit7、代理127.0.0.1:7890不可达：已由用户授权CDP恢复，记录 `tasks/research-2026-10/evidence/network-failure.json`。
- 正式CDP前普通沙箱EPERM；正式申请通过，check-deps返回ready(port3456)、/targets有效。
- 本次新阻塞：读取sitemap1的`/eval`返回HTTP500；详见 `tasks/research-2026-10/evidence/cdp-failure.json`。未获得响应错误body，只有异常堆栈；根因未知。
- 仅创建任务专用标签页；已关闭本次创建页，保留用户页和代理。

| 验收项 | 状态 |
|---|---|
| Q1至少7产品正文证据 | 部分：国内3个/海外2个；国内数量未达标 |
| Q2详情可读+SSR/原始HTTP+条款正文 | 部分：DOM可读/付费截断；SSR与条款未知 |
| Q3四引擎实测推荐+sitemap | SERP因四站robots禁止未执行；根及sitemap1已测，不作引擎质量排名 |
| Q4规则或明确未知 | 已交付规则证据与未知边界；条款许可仍未知 |
| Q5真实JD/帖子/fixture | 未完成 |
| Q6四搜索API官方证据与实测 | 未完成 |
| 对设计的影响 | 已写暂定建议，未实施 |

恢复入口：`tasks/research-2026-10/start.md`。等待用户指引后再诊断同CDP路径；不自行重试联网或切换工具。第一份完成前不开始第二、三份联网调研。

独立只读审阅：PASS（仅部分报告证据一致性），无Critical/Important；2个Minor措辞已修正。审阅记录 `tasks/research-2026-10/review.md`。

## 新规则后的继续检查（2026-10-04）

用户将CDP入口限定为绝对路径`cdp.mjs`，单条执行、无管道、无提权。本次正确格式`targets --filter nowcoder`仍报`EPERM connect 127.0.0.1:3456`；本地`codex execpolicy check`命中现有规则并返回`allow`。这只证明规则文件匹配，不能证明当前执行环境按它放行；运行时原因未知。未取得新的网页，未重试、换工具或修改审批规则。错误与规则验证见`tasks/research-2026-10/evidence/cdp-entrypoint-eperm.json`。此前部分报告的独立review不包含本次新增执行记录；新增记录仅证据化自检。

## 本轮CDP恢复与新阻塞（2026-10-04）

- 平台前缀许可保存后，严格单条默认执行`cdp.mjs targets --filter nowcoder`成功（total38、shown0），已恢复网络入口，未提权。
- 同任务标签页`E720249C4DEBF9F1A7409D37CFAED01A`用于公开资料导航；本轮新增5个产品正文、6个robots页面状态，以及sitemap1原始HTTP统计；多数有真实截图，效招本次只保存DOM，截图未补齐。
- 继续导航搜狗robots前，代理返回`CDP_CONNECT_TIMEOUT: Chrome 调试连接在 20 秒内未获响应；检查授权提示，后续请求可重新连接。`。按用户规则暂停联网，无重试；该批其余超级简历正文、智联/猎聘规则、博查/Tavily/SerpAPI规则均未执行。错误证据`tasks/research-2026-10/evidence/cdp-connect-timeout.json`。
- 已询问用户Chrome是否显示调试授权提示，等待实际情况后继续同入口诊断。调试授权是可能原因，未确认存在弹窗。任务专用标签页暂保留待恢复，不关闭用户标签页。
- 本轮新增内容仅证据化自检，首轮PASS不能覆盖新增结论。原始三份调研仍未完成。

本轮Q1/Q3独立只读审阅PASS，无Critical/Important；两项Minor（历史/最新阻塞与两轮证据结构）已修正。未保存完整XML的可复算性缺口保留。PASS只代表新增部分证据一致性，不是三份调研整体完成。
