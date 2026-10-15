# 合作者交接

当前开发内容在私有仓库 `Lucky-love-wxy/xiaogu-career-suite` 的 `launch-platform` 分支。默认 `main` 是早期版本，下载 ZIP 时也要先切分支。

## 最简交付

仓库所有者在 GitHub 的 Settings → Collaborators 添加合作者的 GitHub 账号。协同开发授予必要写入权限，合作者接受邀请后执行：

```bash
git clone --branch launch-platform https://github.com/Lucky-love-wxy/xiaogu-career-suite.git
cd xiaogu-career-suite
```

后续改动用各自分支提交和 Pull Request 合并。只需体验产品时，交付已部署网站地址和邀请码即可，不需要仓库权限；本文没有核验线上站点是否可用。

## 内容入口

- `web/`：agent 核心和服务端 harness。
- `skills/`：可独立安装的 Skill、提示词、资料与校验脚本。
- `platform/`：账号、额度、存储、用户页面和部署。
- `docs/`、`notes/`、`evidence/`、`tasks/`：设计、研究、证据和任务交接。
- `related/`：插件、演示视频、仓库外资料快照，以原处为维护源。

## 本机启动

先用离线模式确认项目能启动，不产生模型调用费用：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r platform/requirements.txt
XIAOGU_ENV=dev XIAOGU_PROVIDER=mock python platform/app.py --port 8781
```

访问 `http://127.0.0.1:8781/`。离线模式仅用于检查流程，输出不代表真实模型效果。以上依据当前启动入口整理，本次归档没有在全新机器重装验证。

真实模型使用 DeepSeek；合作者自行配置 `DEEPSEEK_API_KEY`，并按 `platform/deploy/env.example` 设置环境变量。不要发送或提交生产密钥、数据库、用户对话。`启动.command` 以及部分脚本包含作者本机路径，其他机器优先用上面的相对路径命令。生产部署另见 `platform/deploy/RUNBOOK.md`。
