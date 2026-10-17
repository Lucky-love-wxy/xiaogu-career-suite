# 岗位理解默认接入实时来源 · 启动文档

## 元数据

- 日期：2026-10-03
- 任务名：岗位理解默认走实时来源（脉脉等），本地库退为兜底
- 所属项目：xiaogu-career-suite
- 触发类型：设计
- 关联 Principle：P1（先看清再下注）；feedback_research_before_build；feedback_evidence_based_claims

## 1. 市场调研结果

### 1.1 用户需求侧（详见 docs/research/job-seeker-core-questions-2026-10-03.md）

- 50.54% 应届生把「不了解岗位」列为求职失败主因之一（中青报 × 粉笔，2025-01，n=1011）。
- 70.2% 认为岗位实际工作内容描述不清；68.4% 认为薪酬含糊、自我拔高；62.7% 认为晋升画饼（中青报 × 问卷网，2023-11，n=1334）。
- 结论：「这个岗位实际干什么」是有数据支撑的核心痛点，JD 本身恰恰是信息不足的那一方，所以只靠 JD + 本地库不够，需要外部从业者信息。

### 1.2 数据源可访问性（2026-10-03 实测 robots.txt 与未登录访问）

| 来源 | 未登录实测 | robots.txt 对 AI 代理的规定 | 适配度 |
|---|---|---|---|
| 脉脉 maimai.cn | 首页 200；`/community/home` 307 跳登录；站内搜索 302 跳登录；`/article/list` 403 | ChatGPT-User、OAI-SearchBot、Perplexity、豆包、Kimi、混元、通义、DeepSeek 等：仅允许公开详情页（`/community/gossip-detail/`、`/article/detail`、`/company`、`/seo/`、`/geo/...`）。**Claude-User / ClaudeBot：全站 Disallow**。默认 `*`：全站 Disallow | 单帖详情可读，站内发现（搜索）需要登录 |
| 牛客 nowcoder.com | 未测页面 | `User-agent: *` 仅禁 `/search` 等少数路径，提供 sitemap | 面经、校招讨论为主，贴合新手大学生 |
| 知乎 | — | `*` 全站 Disallow | 不可用 |
| 小红书 | — | `*` 全站 Disallow | 不可用 |
| BOSS 直聘 | — | `*` 有 Disallow，已有 boss-agent-cli 走用户本人登录 | 现有 xiaogu-boss-jobs |
| 看准网 | robots.txt 返回 SPA 页面，无有效规则 | 未知 | 待查 |

对用户「Codex 调研脉脉不需要登录」的解释：Codex 的抓取身份属于 ChatGPT-User 一类，脉脉对这类代理开放公开详情页；同样的请求以 Claude 身份发出则被 robots 禁止。**能否访问取决于宿主平台的抓取身份**，不是脉脉对所有 Agent 开放。WorkBuddy 使用的抓取身份未知。

### 1.3 同类产品做法（2026-10-05 部分调研回填）

- 已核验国内8个求职工具/平台与海外Teal、Jobscan公开页面，见[调研报告](../docs/research/live-sources-2026-10.md)。效招、牛客AI、超级简历、智联求职AI主要公开招聘文本匹配、简历和题库能力；BOSS/猎聘AI岗位解释未验证。未找到默认引用可追溯员工日常的公开证据，不代表绝对没有。
- 牛客讨论公开DOM部分可读，面经样本有付费截断；单条刷题讨论的无Cookie原始HTTP/SSR正文已核验，自动化条款仍未知。自有XiaoguBot按默认*判断，脉脉不在可用来源内，不能借用宿主白名单身份。
- 五份算法JD全文及截图已保存；新增3条真实来源fixture并通过读取回归；四主题仅定性覆盖，旧帖/年份/身份及同岗位适用范围有限，工时占比和当前同团队证据仍缺。四搜索API官方资料已有部分比较，五查询实际质量待凭证；未完成整体验收，方案第4节仍需按报告中的影响校正。

## 2. 我要解决的问题

（待 1.3 补完后填写）

## 3. 适用的设计规范

- 深度分析规范（业务流程：业务影响、UX 损失、合规影响）
- 小谷事实边界：外部分享只能是 `external_report`，不得进入 JD 事实或候选人事实
- AI 协作 SOP：关键决策点不直接采纳 agent 建议

## 4. 方案草案（用户 2026-10-03 同意先行落地；1.3 回填后校正）

已落地：路由字段 `live_sources`、external-research.md 来源规则、渲染器 external_report 必带链接日期、话术层 skills/xiaogu-career-master/references/phrasing.md、模拟样例 examples/algorithm-engineer-mock/。待用户选：话术决策点 A、B。

1. 岗位理解的默认顺序：JD 原文 → 本地词典与职业库（确定性、零成本）→ 实时来源（默认开启，不需要用户说「脉脉」）。
2. 实时来源失败不阻塞：拿不到就标「从业者反馈未知」，结论仍基于 JD 给出。
3. 只读平台允许的公开页面；发现帖子走公开搜索引擎或 sitemap，不调用需要登录的站内搜索，不使用用户 Cookie。
4. 每条外部内容附链接与发帖日期，最多引用 3 条，标「个人分享，未核实」。
5. 宿主平台抓取身份被禁止时（例如 Claude），自动跳过该来源，不绕过 robots。
6. 来源优先级候选：牛客（规则最宽、校招面经多）与脉脉公开详情页并列，具体顺序等 1.3 补完再定。

### 1.4 搜索 API 实测：Tavily（2026-10-12，Claude）

- 证据：evidence/search-api-2026-10-12/tavily-raw.json、tavily-zhihu-official.json；key 在钥匙串 xiaogu-tavily。共 9 次调用（basic，max_results 10），单次 2.8–3.8 秒。
- 预注册 5 条 `site:nowcoder.com` 查询：site 限定生效，5×10 条全部是牛客页面；标题相关性高（面经、日常、加班、实习、成长），但 published_date 全为空，时效需进详情页判断；混有职位页和话题聚合页。
- 公司背调 3 条：Kanzhun（BOSS直聘上市主体）命中港交所 2024 年度业绩公告 PDF 和 ir.zhipin.com 投资者关系页，质量好；“知乎 主营业务 收入构成 年报”10 条里只有 3 条相关（两篇财经报道、一个知乎回答），没有官方披露；米哈游（非上市）返回维基、百度百科、上海市政府页面，无官网。
- 加 include_domains（hkexnews/sec/cninfo/ir.zhihu.com）反而全是无关 A 股公司的巨潮 PDF：只限域名不识别公司主体。结论：公司背调要先确定“法定主体名 + 上市地/代码”，再按交易所定向搜；非上市公司只能拿到百科和媒体，需标来源等级。
