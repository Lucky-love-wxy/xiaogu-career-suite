# fetch_public.py 安全审查修复

## 元数据
- 日期：2026-10-13
- 任务名：fetch_public.py 安全审查三项修复
- 所属项目：xiaogu-launch（分支 launch-platform，commit 26678b4 从 sim 迁入）
- 触发类型：debug（安全）
- 关联 Principle：暂停编号（全局 CLAUDE.md 2026-10-03 暂停项）
- 触发 systematic-debugging skill：是（按 现象 → 复现 → 假设 → 排除 → 根因 走）

## 现象
推送后自动安全审查对 `tasks/industry-clusters-20261011/fetch_public.py` 报 3 条：
1. 路径穿越 / 任意文件写
2. URL scheme 不受限导致 SSRF / 本地文件泄露
3. 第三条通知里没显示

## 复现（静态读码）
- 第 9 行：`p=pathlib.Path(x['path'])` 直接取 manifest 值，未做任何约束，随后 `mkdir` + `write_bytes`。`../../x`、`/abs/x` 都能写到任意位置；`cached` 分支还会读取并哈希任意已存在文件。
- 第 27 行：`urlopen(u)` 对 `file://`、`ftp://` 照收，`file:///etc/passwd` 会被读出并写进输出文件。
- robots 文件名用 `h`（netloc）拼在 `p` 同目录，随路径穿越一起越界。

## 假设清单（第三条）
- A：重定向跟随——urllib 默认 HTTPRedirectHandler 允许跳到 `ftp://` 和任意主机（含内网），绕过 scheme 白名单，也绕过按主机的 robots/停站判断。**采纳**，否则修复 2 不完整。
- B：`resp.read()` 无上限，大响应吃内存。弱候选，未修（保持最小改动），在报告里列出。

## 已排除项
- GitHub commit comments：`[]`；code-scanning：仓库未开启（403）。第三条无法确认原文，为推断。

## 根因
脚本是 sim 时期的一次性采集脚本，把 manifest 当可信输入：URL 和输出路径都无校验，且依赖 urllib 默认重定向行为。

## 修法
- 锚定输出根：`ROOT/evidence/industry-clusters-2026-10`（与同目录 build_tables.py 等一致），`(base/path).resolve()` 必须 `is_relative_to(base)`；绝对路径在 `/` 运算下会替换 base，同样被拦。
- URL 仅允许 http/https 且 netloc 非空。
- 自建 opener，重定向目标非 http/https 直接拒绝；robots 请求也走这个 opener。
- 所有校验放在 mkdir 等副作用之前；失败记 `rejected_url` / `rejected_path` 并 continue，results.json 保持完整。

## 遗留 / 待用户决定
- 两个历史 manifest 的 `path` 仍是 `xiaogu-career-suite/evidence/...` 前缀（迁移时漏改）。新锚点下会写到 `base/xiaogu-career-suite/evidence/...` 的嵌套目录，不会越界但位置不对。未改，等用户决定。
- 同类问题的兄弟脚本见对话报告，未修。

## 验证（离线，2026-10-13）
- 8 条恶意 manifest（file://、ftp://、空 host、`../` 穿越、绝对路径 ×2、`examples/../../`、`.`）全部 rejected_url / rejected_path；evidence/ 下无新文件，越界位置无文件；代理指向死端口，未发生网络请求。
- 直接调用 `SafeRedirect.redirect_request`：ftp:// 与 file:// 被拦，https 放行；opener 已用 SafeRedirect 替换默认重定向处理器。
- 未覆盖：重定向到同 scheme 的内网主机（http://127.0.0.1 等）仍会跟随，跨主机重定向也不再查 robots；`resp.read()` 无上限。脚本只吃自己写的政府站 manifest，暂不处理。

## 后续（2026-10-13，用户确认后）
- 两个 manifest 的 path 去掉 `xiaogu-career-suite/evidence/industry-clusters-2026-10/` 前缀，改为相对 evidence 目录；software 重跑命中 cached。examples 两条当时 403 未下载，本就无文件。旁边的 .results.json 是历史记录，未改。
- state-employer 的 collect.py 同样加 scheme 白名单 + SafeRedirect；supplement / extra_entries / collect_identity 通过 exec 复用 fetch，一并生效。离线测 file:// / ftp:// / 空 host 均 rejected_url，snapshots 目录数不变。
