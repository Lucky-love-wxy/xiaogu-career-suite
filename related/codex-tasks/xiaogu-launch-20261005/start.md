# 小谷大陆上线执行

- 任务标识：xiaogu-launch-20261005；恢复入口：/Users/lucky_wang/Documents/codex/tasks/xiaogu-launch-20261005/start.md
- 原始目标与验收：按 /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/deploy/RUNBOOK.md 推进中国大陆上线；用户要求“开始吧，需要我操作的停下来并且告诉我在哪里”。不是单纯部署脚本运行：须完成域名/备案、真实登录与模型、协议与适用手续、测试及授权生产发布、真实设备体验验收。
- 最新用户修正：选择阿里云；已付68元购买上海Ubuntu24.04的2核2G/40G服务器；希望可复用多个域名/项目；要求“你来完成吧”；域名名字答复“xiaogu”。
- 用户授权：服务器必要配置/代码传输及测试部署已授权，保留原项目未提交改动，不自动commit/push；付款、证件/实名、主体承诺和具体域名选择由用户参与；不发送邀请码、不撤销仍被其他项目使用的模型key、不扩大到其他实例/项目。
- 项目：/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch（修改该目录已逐次获平台批准）；任务工具位于 /Users/lucky_wang/Documents/codex/tasks/xiaogu-launch-20261005/scripts/。
- 服务器：Ubuntu-kyuv / e81e60e53db34b3bb18570261a65a5ee / cn-shanghai / 106.14.236.108；到期2027-10-05 23:59:59。专用SSH密钥位于 /Users/lucky_wang/.ssh/xiaogu-launch-aliyun-20261006（600，不入Git），主机指纹通过阿里云命令助手与SSH独立比对一致；known_hosts见 evidence/ssh-known-hosts。
- 已完成：基础Python3.12.3/SQLite/venv工具安装，xiaogu专用用户与目录；通过命令助手配置专用SSH公钥，保留旧authorized_keys；白名单打包并只部署localhost/mock staging。
- 实际服务：xiaogu@staging active，只监听127.0.0.1:8102；发布 staging-6d7b7453b30da55d；/etc/xiaogu/staging.env为600/root，随机秘密仅在服务器，不输出；未安装Nginx，未开放公网网页，未部署prod。
- 修复：deploy/env.example行尾注释（前轮）；web/auth.py保留邮箱连字符/加号，tests/test_platform.py增加真实邮箱注册回归。23平台测试通过；首次部署前110项及66子检查通过（更早baseline）。
- 实际服务器验收：8项PASS，含staging/mock、未登录拦截、Secure cookie、邀请注册与console登录、mock聊天零扣费、跨账号会话隔离、登出、SQLite完整性。测试客户端模拟TLS终止以访问localhost HTTP；不是HTTPS或真机验收。仅生成虚拟测试账号。
- 证据：evidence/staging-acceptance.json、evidence/runtime/runtime-manifest.json、evidence/email-normalization.diff、evidence/review-20261006.md；独立只读review对本批次PASS（整体生产仍未就绪）。
- 恢复资产：旧包 evidence/runtime-staging-974a9df85fd53d7c.tar.gz；服务器/root/runtime.tar.gz同旧包；更新前在线DB备份 /var/backups/xiaogu/staging-pre-staging-6d7b7453b30da55d.db，完整性与600/root已核验。失败时停止服务、保留当前DB，恢复旧包后再验收；不默认恢复旧业务DB。
- 当前本人停点：域名实名信息模板。xiaogu.com已注册；xiaogu.cn转售23000元；xiaogu.net在搜索页看似可注册，但结算页提示工信部黑名单不能注册，未提交。两个有效结算候选：myxiaogu.com首年85元（续费未核验）；xiaogu.net.cn首年38元（搜索页续费42元/年）。详见 evidence/domain-check.json。
- 已打开：Chrome xiaogu.net.cn购买页的“创建信息模板”弹窗，未填写证件/联系信息、未提交/付款。用户需选择实际个人或企业主体、上传证件、填真实联系方式并完成邮箱验证；不要求把证件发聊天。target=0A5681C8130D60DCF6DB3294F5E2A8C8，URL=https://wanwang.aliyun.com/buy/commonbuy?domainCartTradeParams=dr_29379033_1791225187350&domain=xiaogu.net.cn&duration=12；myxiaogu.com候选target=5DED457C5AAB2C2FA6AE068D078CC846。
- 剩余：确认域名并购买/实名认证/备案，TLS/Nginx；验证码方式异步问题仍待回答（邮箱或短信），真实Sender实现/未知名字拒绝；旧模型key安全轮换/接新key；协议主体和实际数据用途确认；模拟来源关闭/合法真实来源；AI上线手续适用核验；生产发布安全版本/回滚/敏感路径排除；可靠每日备份和恢复演练；真机与真模型验收。
- 下一步：用户完成实名模板并确认域名后，读回模板状态和最终单域名订单，停在由用户付款；不要误点加购AI建站/备案管家/第二台ECS。与此同时推进不依赖个人输入的已授权技术项。
- 状态：进行中，当前依赖本人实名与域名确认；未声称已上线。最后更新：2026-10-06 02:39 Asia/Shanghai。
- 历史流水入口：evidence/start-before-20261006.md（只作已完成事实，不产生额外授权）。

- 域名补充：用户询问xiaogu.icu首年10元是否合适；已核对有效结算项首年10元，搜索页续费125元/年，结算提示暂不能在北京备案。等待备案主体所在省份；上海服务器不等于上海备案主体。未下单/付款。证据见evidence/domain-check.json。

- 最新修正（2026-10-06 12:11）：个人备案，浙江，计划只运营一年。按首年价格建议xiaogu.icu；阿里云浙江规则未列出.icu特别限制，全国获批后缀包含ICU，备案审核仍待实际提交。已在Chrome前台打开xiaogu.icu购买页个人实名模板（target=6BDC9242836954A563EA81C3489D744F），未填/提交证件、未下单/付款。当前本人操作：填写真实个人实名信息并完成邮箱验证，随后确认只买1年域名10元。若身份证住址非浙江需浙江暂住/居住证。

- 支付后核验（2026-10-06 12:16）：xiaogu.icu已注册，2026-10-06 12:14:18注册，2027-10-07 07:59:59到期；域名状态未实名。现有个人模板未实名且邮箱待验证。Chrome前台展示信息模板页（D86E3855300212A6E91DE66C284CD4BC，https://dc.console.aliyun.com/next/index#/info-stencil/infoStencil）。需要本人完成实名材料及邮箱验证，完成后再核对域名实名和备案等待期；未配置DNS、未开放公网网站。未修改持有者或默认模板。

- 实名提交跟进（2026-10-06 13:08）：用户答复已提交；核验模板状态的CDP调用返回CDP_CONNECT_TIMEOUT，Chrome连接20秒未响应。用户提交事实与平台审核结果区分，最新审核/邮箱/域名同步状态未知，未改DNS或提交备案。按用户联网失败规则暂停联网，不切换路径；请用户检查Chrome授权提示并恢复连接后再读取。

- 恢复核验（2026-10-06 13:17）：CDP已恢复；刷新信息模板后邮箱验证成功，模板仍未实名，域名列表仍未实名，未见审核中/成功提示。用户之前答复提交了，需确认是邮箱验证还是证件实名提交；不能推断已实名。模板“查看”点击未出现可核验详情；官方旧认证文档URL返回Internal Error/不可访问，按失败规则停止联网，未切换访问路径。当前依赖：确认用户实际提交类型/阿里云实名提交凭据，不索取证件号码。
