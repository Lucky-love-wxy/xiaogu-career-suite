# related：仓库外的小谷相关文件（快照）

2026-10-14 按用户要求把散在仓库外的小谷相关文件一起放上 GitHub。这里是**复制的快照**，原件还在原处、仍以原处为准（原处被 Codex 任务、视频工具链等按路径引用，不能搬）。原件更新后需要重新复制。

| 目录 | 原处 | 内容 |
|---|---|---|
| xiaogu-motion/ | /Users/lucky_wang/Documents/codex/xiaogu-motion | Codex 做的小谷动效页 |
| codex-tasks/2026-10-04-xiaogu-launch/ | /Users/lucky_wang/Documents/codex/tasks/2026-10-04-xiaogu-launch | Codex 任务交接（上线文档） |
| codex-tasks/xiaogu-launch-20261005/ | /Users/lucky_wang/Documents/codex/tasks/xiaogu-launch-20261005 | Codex 任务交接（上线平台、阿里云部署） |
| notes/ | /Users/lucky_wang/Documents/Claude/notes | 小谷专属笔记：开源案例借鉴点、Glassdoor 职位与简历匹配逆向（含 brief）、公众号引流稿 |
| demo-video/xiaogu-30s/、xiaogu-15s/ | /Users/lucky_wang/Documents/Claude/projects/product-demo-video/videos | 小谷产品演示视频工程与成片（30s 的逐帧中间图 rec/frames/ 共 3589 张、122MB，可重新生成，未上传） |

没有上传的：用户的书籍和学习日志；开发数据库 web/data/（含测试账号和用户本人的试用对话）；运行日志 web/logs/（含用户原话）；个人简历和面试记录（profile/、interviews/、jobs/raw/）。

## 2026-10-15 补充快照

- `xiaogu-jargon-extension/`：Claude/projects/xiaogu-jargon-extension 的完整源码、测试和设计/排查笔记快照。
- `demo-video/xiaogu-screencast/`：2026-10-15 演示工程、成片、素材与来源许可；演示引用的 JD 和模型回答属于演示材料。
- `demo-video/notes/`：15 秒宣传片与 30 秒真机录屏设计记录。

这些目录保留原始文件内容。插件构建/一致性测试及部分视频脚本包含作者本机绝对路径，异机运行前需按实际目录调整；直接加载已生成的 `xiaogu-jargon-extension/extension/` 不需要重新构建。协作入口见 `docs/collaborator-handoff.md`。
