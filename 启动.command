#!/bin/bash
# 双击启动小谷上线版（本机开发，端口 8781，已在 ports-registry.json 登记）。关掉本窗口即停止服务。
cd /Users/lucky_wang/Documents/Claude/projects/xiaogu-launch
PORT=8781
# 上次没关干净的进程会占住端口，先清掉再起，避免新旧两个实例冲突
OLD=$(lsof -ti tcp:$PORT -sTCP:LISTEN)
[ -n "$OLD" ] && echo "端口 $PORT 被占用（PID $OLD），先结束旧进程" && kill $OLD && sleep 1
(sleep 3 && open "http://127.0.0.1:$PORT/") &
XIAOGU_ENV=dev XIAOGU_PROVIDER=deepseek XIAOGU_MODEL=deepseek-flash \
XIAOGU_ADMIN_TOKEN=dev-admin \
exec .venv/bin/python platform/app.py --port $PORT
