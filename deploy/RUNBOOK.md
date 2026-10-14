# 小谷上线手册（中国大陆）

日期：2026-10-05。对应设计：`notes/2026-10-05-launch-platform-design.md`。

代码已经能部署，但「上到中国互联网」有几步只能你本人办（花钱、实名、提交备案）。下面按顺序列出，每步标明谁做、多久、做完的标志。

## 0. 上线阻塞项（任一没解决就不能对外开放）

| # | 阻塞项 | 现状 | 谁 |
| --- | --- | --- | --- |
| B1 | 域名 ICP 备案 | 未开始。没备案，境内服务器的 80/443 不能对外 | 你 |
| B2 | 登录验证码发送 | 只有 console（验证码打在服务器日志里），prod 会拒绝启动 | 你选服务商 + 我接代码 |
| B3 | 用户协议 / 隐私政策 | 草稿，带 DRAFT 标记，prod 会拒绝启动 | 你确认内容 |
| B4 | DeepSeek key | 旧 key 在对话里明文出现过 | 你在 DeepSeek 后台轮换 |
| B5 | 从业者来源是模拟数据 | `agent.py` 的实时来源仍读 `examples/` 下的模拟帖子；界面会标“模拟数据”，但不该出现在给真实用户的产品里 | 我（关掉或接真实源，需你定） |
| B6 | 生成式 AI 上线登记 | 需要营业执照；邀请制内测是否可以先不登记，要问属地网信办或代办 | 你 |
| B7 | 模型走第三方中转站（2026-10-06 改为 new.tornadorouter.com） | 用户对话和简历会经过一家第三方；它不是已备案的大模型服务，页脚无法如实公示备案号；域名解析到 179.0.0.0/8（拉美地址注册机构管理的地址段，服务器所在国未核实），可能构成个人信息出境。prod 默认拒绝启动，显式设 `XIAOGU_ALLOW_THIRD_PARTY_ROUTER=1` 才放行 | 2026-10-06 已决定：生产用 DeepSeek 官方，不走中转站。中转站支持代码保留（开发可用、生产默认拒绝） |

B1、B4 是硬前提；B2、B3 由代码强制检查；B5、B6 需要你做决定。

## 1. 你要做的（按顺序）

1. 选云厂商（腾讯云或阿里云，选了就别换，备案跟着走），买一台轻量服务器：2 核 4G、Ubuntu 24.04、地域选离你近的境内地域。
2. 在同一家买域名，完成域名实名认证。
3. 在云厂商控制台提交 ICP 备案（个人备案即可开始；收费上线要企业主体）。一般 1–3 周。备案期间网站不能对外访问，但服务器可以先部署、用 IP + 端口转发自己看。
4. DeepSeek 后台：删除旧 key，新建两把：prod 一把；staging 一把并在后台设低额度（如果 DeepSeek 后台支持单 key 限额；不支持就只给 staging 用模拟模型）。
5. 生成两个密钥：`openssl rand -hex 32`（XIAOGU_SECRET）、`openssl rand -base64 24`（后台口令），存进密码管理器。
6. 决定登录验证码服务：阿里云 / 腾讯云短信（个人能否申请签名待核实），或企业邮箱 SMTP。告诉我选哪个，我接 `web/auth.py` 的 Sender。
7. 通读 `web/static/legal-terms.html`、`legal-privacy.html`，填好方括号，删掉 `<!-- DRAFT` 那一行。

## 2. 部署（我可以陪你做，命令都在本机运行）

```bash
/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/deploy/deploy.sh bootstrap ubuntu@你的服务器IP
```

然后在服务器上：

1. 按 `deploy/env.example` 写 `/etc/xiaogu/staging.env`（PORT=8102，不写 XIAOGU_PROVIDER 即用模拟模型）和 `/etc/xiaogu/prod.env`（PORT=8101、XIAOGU_ENV=prod、DEEPSEEK_API_KEY、XIAOGU_ICP_NO 等），`chmod 600`。
2. 把 `deploy/nginx.conf` 放到 `/etc/nginx/conf.d/xiaogu.conf`，替换域名和证书路径；`htpasswd -c /etc/nginx/xiaogu-staging.htpasswd 用户名` 给测试环境加口令；`nginx -t && systemctl reload nginx`。
3. 证书：云厂商控制台申请免费 DV 证书，下载 nginx 格式放到 `/etc/nginx/certs/`。

发布：

```bash
/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/deploy/deploy.sh staging ubuntu@你的服务器IP
```

到 `https://staging.你的域名` 手动走一遍（第 4 节清单），没问题再：

```bash
/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/deploy/deploy.sh prod ubuntu@你的服务器IP
```

生产只会复制测试环境里正在跑的那一版。

## 3. 上线当天

1. 打开 `https://你的域名/admin`，用后台口令登录。
2. 「阈值」里确认：扣费倍率 1.0、当日成本上限（建议先 ¥20）、DeepSeek 余额下限（建议 ¥20）。
3. 「邀请码」生成第一批（例如 20 个、每码 100 credits（≈ 后台 ¥2）、可用 1 次、备注写渠道），发给内测用户。
4. 盯第一天：看「质量」的受阻率和耗时、「用户」里每人的成本。出问题点顶栏「运行中」一键停止。

## 4. 每次发布的手动验收清单

在 iPhone Safari、安卓 Chrome、微信内置浏览器各走一遍：

- 主页 → 开始使用 → 登录（新用户要邀请码和勾选协议）→ 进入对话页，右上显示额度
- 问一句黑话 → 有回答，额度减少（真模型）或不变（模拟模型）
- 贴一份简历 → 生成成品页链接，能打开；换个账号打不开同一链接
- 说「模拟面试」→ 能答题、说「结束」能打分
- 输入框不被遮挡、点输入框页面不自动放大、没有横向滚动
- 后台：今日成本、用户列表、对话抽屉（手机号已打码）、全局停止后用户看到暂停提示，恢复后正常

## 5. 日常

- 每天：后台扫一眼盈亏和质量。
- 每周：DeepSeek 官方价格页对一次单价（后台「单价」）；`/var/backups/xiaogu` 有每日备份。
- 看日志：`journalctl -u xiaogu@prod -f`。
- 本机开发：

```bash
cd /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch && XIAOGU_ENV=dev XIAOGU_PROVIDER=deepseek XIAOGU_BASE_URL=https://new.tornadorouter.com/v1 XIAOGU_ADMIN_TOKEN=dev-admin .venv/bin/python web/app.py --port 8781
```

然后打开 http://127.0.0.1:8781 （后台 /admin，口令 dev-admin；开发环境验证码会直接显示在登录页上）。
