# 公司背调试点脚本

范围为 2026-10-12 的 6 家公司研究，不接入小谷运行时。Python 3 + 系统 `pdftotext`，其他均标准库。

- `collect.py search <plan.json>`：basic Tavily搜索；从钥匙串 `xiaogu-tavily` 只在进程内读取key，先记尝试数，最多60次API调用。`usage <新标签>`读账户额度，不把账户读数等同响应记账。
- `collect.py fetch <plan.json>`：不使用Cookie，先查robots；不自动跟随重定向；共享域名限速至少3.1秒，明确HTTP/验证码/混淆挑战信号即停当日网站。未知robots不访问目标。计划是本目录 `search-*.json`/`fetch-*.json`，已有id快照断点复用。
- `build.py`：离线从原始证据构建6卡、渠道观察、清单；短摘必须在原文中，不超过30字符；财务金额/报告期/审计属性为审阅过的编辑输入。
- `report.py`：从卡片、来源、渠道和额度快照渲染报告及来源CSV。
- `validate.py`：无网络/无key；核对引用、短摘、SHA、收入算术、字段、日期及预算；用真实挑战响应测试守卫、根域停止/限速、预算、robots和重定向。

```sh
python3 scripts/companycheck/build.py
python3 scripts/companycheck/report.py
python3 scripts/companycheck/validate.py
```

原始证据在 `evidence/company-check-2026-10/`，由项目已有ignore规则排除。报告在 `docs/research/company-check-pilot-2026-10.md`，数据在 `data/companies/`。执行与恢复状态在 `tasks/company-check-20261012/start.md`。

当前脚本是研究工具，不能保证识别所有反爬信号；可疑/无主体正文应由人工按fail-closed审查。历史首轮停站识别偏差保留在报告中，修正后的离线守卫通过不意味着首轮已满足网络协议。CDP是人工选择的公开页补充取证，未实现统一匿名浏览和自动停站控制，不把脚本fetch限制扩张为全链路保证。
