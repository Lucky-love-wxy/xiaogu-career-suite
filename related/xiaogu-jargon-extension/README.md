# 小谷黑话（Chrome 插件）

把小谷求职 agent 的招聘黑话库独立出来：在招聘网站上自动高亮黑话，点一下看它没明说的意思、可以怎么问 HR、什么回答才算具体。纯本地匹配，不调用大模型，不上传页面内容。

## 安装

1. Chrome 打开 `chrome://extensions`，右上角开「开发者模式」。
2. 点「加载已解压的扩展程序」，选 `/Users/lucky_wang/Documents/Claude/projects/xiaogu-jargon-extension/extension`。

## 使用

- BOSS 直聘、猎聘、智联、前程无忧、拉勾、实习僧、牛客、脉脉：打开页面自动高亮。
- 其他网站：点工具栏的插件图标，在当前页开启；再点一次关闭。
- 右下角「谷」印章显示本页命中数，点它开关高亮。
- 点高亮词弹出浮窗：默认显示露骨翻译、可以这样问、证据边界；其余（字面意思、最坏情况、危险信号、合格回答）折叠。

## 数据来源

唯一来源：`/Users/lucky_wang/Documents/Claude/projects/xiaogu-launch/skills/xiaogu-career-suite/references/jargon.json`。词库更新后双击 `更新词库.command`（重新生成 `extension/data.js` 并跑测试），再到 `chrome://extensions` 刷新插件。不要手改 `data.js`。

## 匹配规则

与 xiaogu-launch 的 `search.py` 一致（忽略大小写、字符间允许空白），另加：长词优先占位；否定词紧贴在命中前（如「非双休」「没有团建」）时跳过，「非常」「不断」「不定期」这类复合词不算（词条本身含否定的除外）。不处理被 HTML 标签拆开的词。

## 测试

```bash
cd /Users/lucky_wang/Documents/Claude/projects/xiaogu-jargon-extension && node --test tests/*.test.js && python3 tests/parity.py
```

设计记录：`notes/2026-10-14-黑话浏览器插件.md`。
