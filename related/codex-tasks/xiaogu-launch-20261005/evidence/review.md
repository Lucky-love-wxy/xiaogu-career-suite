# 独立只读上线审阅

结论 NEEDS_CHANGES（整体上线仍未就绪）。

- Important：env.example 行尾注释会进入 systemd 配置值，本轮已修复，配置值一致已自检，独立复核 PASS；仅注释中的示例仍含行尾说明，启用时需先拆开。
- Important：app.py 仅校验 sender 字符串，Platform 默认仍 ConsoleSender；真实发送器尚未实现。
- Important：生产因模拟来源门禁不能启动，需关闭或合法真实来源，不能简单删除门禁。
- Important：备份 shell 可掩盖 sqlite 失败；备份目录和文件权限需收紧，失败不得清理旧备份。
- Important：RELEASE 在部署成功前写入；生产只检查文件，不证明测试版本正运行；原位覆盖缺发布前可恢复版本。
- Important：rsync 不遵循 .gitignore，敏感路径排除不完整，需发布文件清单审查。
- Minor：健康检查固定等待 2 秒且仅校验 env；数据库恢复未实测；http2 on 须按服务器 Nginx 版本验证。

本审阅由 launch_review 子 Agent 执行，不修改产物；未在真实 Linux 服务器验证。
