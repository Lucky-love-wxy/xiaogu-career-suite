#!/bin/sh
# 一键出片：sh build.sh [pitch|user]（不带参数两版都出）
#   pitch 路演版：含「运行记录」面板，展示内部流程 → out/video-pitch.mp4
#   user  用户版：不开面板（真实产品里普通用户看不到它）→ out/video-user.mp4
# 每一版：改写 variant.js → 字体子集 → 导出画面声音事件 → 生成配乐与拟音 → 渲染 → 验收。
# --limit 0.55：本片瞬态多（芯片音、镲片、whoosh），默认 0.7 时 AAC 后真峰值过冲到 -0.6 dBFS，压到 0.55 后为 -2.7 dBFS。
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TK="$HERE/../../toolkit"
node "$TK/scripts/fonts.mjs" "$HERE"
for V in ${1:-pitch user}; do
  case "$V" in pitch|user) ;; *) echo "用法：sh build.sh [pitch|user]"; exit 1;; esac
  printf "// 出哪一版：'pitch' 路演版（含「运行记录」面板，展示内部流程）/ 'user' 用户版（真实产品界面里普通用户看不到这个面板）\n// build.sh 按参数改写本文件，不用手改\nexport const VARIANT = '%s';\n" "$V" > "$HERE/variant.js"
  echo "== $V"
  node "$TK/scripts/events.mjs" "$HERE"
  sh "$TK/audio/run.sh" "$HERE"
  node "$TK/scripts/render.mjs" "$HERE" --limit 0.55 --out "$HERE/out/video-$V.mp4"
  sh "$TK/scripts/check.sh" "$HERE/out/video-$V.mp4"
done
