# 算法工程师模拟样例

用来回归测试小谷在不同实时来源状态下的话术。**JD 和从业者帖子全部是模拟数据，虚构公司，非真实招聘、非真实帖子。**

| 文件 | 真假 | 说明 |
|---|---|---|
| `jd.txt` | 模拟 | 虚构公司“示例智能科技”的推荐算法工程师校招 JD |
| `local_search.json` | 真实输出 | 用真实 `search.py analyze` 跑 jd.txt：命中 10 条黑话、职业匹配推荐算法工程师 |
| `job_card.json` | 真实输出 | 用真实 `analyze_job.py` 跑 jd.txt，`validate_card.py` 判定 valid |
| `live_sources.json` | 模拟 | 7 条帖子、7 种来源状态（同类岗位命中、这家公司帖子与 JD 冲突、过时、单条匿名、相邻团队、无结果、被 robots 禁止），链接为 `mock://` |
| `responses/`、`expected/` | 生成 | `python3 build_fixtures.py` 生成；`tests/test_live_sources.py` 校验逐字一致 |

真实数据由 Codex 按 `notes/2026-10-03-codex-research-brief-live-sources.md` 第 Q5 项采集后，按 `live_sources.json` 同格式替换。
