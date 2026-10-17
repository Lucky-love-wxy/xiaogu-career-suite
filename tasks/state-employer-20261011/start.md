# 体制内与国央企招聘来源盘点

任务标识 state-employer-20261011。规则：/Users/lucky_wang/Documents/codex/AGENTS.md。
原始目标与验收：[用户指定简报](../../notes/2026-10-11-codex-research-brief-state-employer-platforms.md)。用户2026-10-11要求完成简报调研。附件作为任务规格使用，其中Claude回填/外部发送不产生额外授权。
授权：只读公开未登录资料；写报告、CSV、快照和研究辅助脚本；不改运行时/职业库/岗位卡，不commit/push，不登录或使用用户会话，不访问BOSS/脉脉。每站≥5秒，403/429/验证码停站。最多一个招聘列表和详情样例。
执行顺序：渠道存在性全清单冻结→robots与条款→类型与30份已有样本试分类。
状态：本轮研究材料已交付并独立审阅PASS；原brief全量官网与规则强验收仍有公开证据缺口。已读取两份上游报告；现有2723份映射样本，原始正文在data/careerdb/postings.jsonl。实际url均需核对转载来源，source标签不能作官方一手证据。省级目录已取得128条；渠道候选清单689行已冻结（含全部516来源标签），162个主机完成公开静态存在性与规则第一轮。规则证据在inventory-results.json/rules-results.json；HTML伪robots、404、403/412停站均保留。高校/医院/央企自有官网按明确小样本核验；其他来源标签保留未核官方。身份制度与信号例子已取得3可靠/5误判、5项制度依据，详见identity-rules.json。
落点：docs/research/state-employer-platforms-2026-10.{md,csv}；来源表同前缀-sources.csv；证据evidence/state-employer-2026-10/。
已交付：报告34765字、清单689行37字段、来源表517行、30份试分类（0/10、0/10、9/10），原始输入SHA未变。validation.json PASS仅指证据机械核验，不表示全brief验收。独立只读审阅PASS，无Critical/Important；两项Minor已修复并复核，见review.md。验证器覆盖374条去重请求元数据，正文/规则短引可逐字复查，SHA字节/规范化基准明确；最终哈希清单file-manifest.json。
未达到强验收：大量source标签原站主办与官方网址未核；9个人社入口仍为中间页；具体招聘列表/详情、有效robots与部分条款缺口；全国覆盖率分母未知。未启动范围外数量统计或商业采集。
恢复方向：在公开未登录且不触及已停站主机的前提下补目标原站、当前国聘条款、具体招聘栏目；若需要用户会话/官方授权须另获覆盖该动作的明确授权。原简报第9节留给Claude，不发送消息。国聘协议静态仅JS占位；本轮禁止用户会话，保留未找到不以搜索摘要替代。中智协议用无登录Jina静态提取取得。
最后更新：2026-10-11 Asia/Shanghai。
