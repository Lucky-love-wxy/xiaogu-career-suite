# 小谷网页动效

- 任务：xiaogu-motion-20261006；工作区规则：`/Users/lucky_wang/Documents/codex/AGENTS.md`。
- 原始要求：为用户提供的小谷角色设定图做网页版动效。
- 授权：新建独立本地演示页、实现并验证交互；未授权线上发布或修改既有求职产品。
- 方案：参考角色比例重绘可动画 SVG；暖白 #F5F4F0、炭黑 #202220、灰 #8B8E86、小芽绿 #DCE7BA；Avenir Next / PingFang SC；左右错位布局。
- 验收：呼吸、眨眼、目光跟随，五种状态，暂停、速度与昼夜切换；键盘与移动端可用；减少动态偏好可用。
- 状态：完成；本地文件已实现。Chrome 前台 19 项交互检查通过，390px / 320px 响应式无横向溢出。验收与截图见 `design-qa.md`、`evidence/`。
- 运行：本次启动 `python3 -m http.server 8792 --bind 127.0.0.1 --directory /Users/lucky_wang/Documents/codex/xiaogu-motion`；预览 `http://127.0.0.1:8792/`。也可直接打开 index.html。
- 完成边界：独立动效演示，未接入原求职产品、未线上发布。无必要剩余任务。
- 最后更新：2026-10-06 14:35 Asia/Shanghai。
