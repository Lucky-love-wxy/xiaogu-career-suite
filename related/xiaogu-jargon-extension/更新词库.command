#!/bin/zsh
# 从小谷权威词库重新打包插件数据，并跑单测与一致性检查。
# 跑完后到 chrome://extensions 点「小谷黑话」的刷新按钮生效。
cd "/Users/lucky_wang/Documents/Claude/projects/xiaogu-jargon-extension" || exit 1
python3 build.py && node --test tests/*.test.js && python3 tests/parity.py
echo
echo "完成。到 Chrome 的 chrome://extensions 页点「小谷黑话」的刷新图标。"
