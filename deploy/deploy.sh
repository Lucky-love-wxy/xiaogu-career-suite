#!/usr/bin/env bash
# 小谷发布脚本。在本机运行，通过 ssh 操作服务器（需要该账号有 sudo）。
#
#   deploy/deploy.sh bootstrap user@host   首次：建用户、目录、装依赖、装 systemd 和备份定时器
#   deploy/deploy.sh staging   user@host   本机跑测试 → 同步代码到测试环境 → 重启 → 自检
#   deploy/deploy.sh prod      user@host   把服务器上测试环境当前这一版原样复制到生产 → 重启 → 自检
#
# 生产只接受“测试环境里已经跑着的那一版”，不直接从本机推生产。
# 未在真实服务器上执行过（2026-10-05 编写时本机没有 Linux 环境），首次使用请逐步看输出。
set -euo pipefail

MODE="${1:-}"; HOST="${2:-}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PIP_INDEX="${PIP_INDEX:-https://mirrors.aliyun.com/pypi/simple/}"  # 国内服务器访问 PyPI 慢，默认用阿里云镜像

[ -n "$MODE" ] && [ -n "$HOST" ] || { sed -n '2,9p' "$0"; exit 1; }

remote() { ssh "$HOST" "$@"; }

health() {  # 服务起来后查 /api/meta，确认环境和模型
  local env="$1" port="$2"
  sleep 2
  remote "curl -fsS http://127.0.0.1:$port/api/meta" | python3 -c "import json,sys; m=json.load(sys.stdin); print('自检通过：env=%s provider=%s model=%s maintenance=%s' % (m['env'], m['provider'], m['model'], m['maintenance'])); sys.exit(0 if m['env']=='$env' else 1)"
}

install_env() {  # 在服务器上为某个环境建虚拟环境、装依赖
  local env="$1"
  remote "sudo -u xiaogu sh -c 'cd /opt/xiaogu/$env && ( [ -x .venv/bin/python ] || python3 -m venv .venv ) && .venv/bin/pip install -q -i $PIP_INDEX -r web/requirements.txt'"
}

case "$MODE" in
  bootstrap)
    remote "sudo sh -c '
      set -e
      apt-get update -qq && apt-get install -y -qq python3 python3-venv nginx sqlite3 rsync curl apache2-utils
      id xiaogu >/dev/null 2>&1 || useradd --system --home /opt/xiaogu --shell /usr/sbin/nologin xiaogu
      mkdir -p /opt/xiaogu/staging /opt/xiaogu/prod /var/lib/xiaogu/staging /var/lib/xiaogu/prod /etc/xiaogu
      chown -R xiaogu:xiaogu /opt/xiaogu /var/lib/xiaogu
      chmod 700 /etc/xiaogu
    '"
    scp "$ROOT/deploy/xiaogu@.service" "$ROOT/deploy/xiaogu-backup.service" "$ROOT/deploy/xiaogu-backup.timer" "$HOST:/tmp/"
    remote "sudo mv /tmp/xiaogu@.service /tmp/xiaogu-backup.service /tmp/xiaogu-backup.timer /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable --now xiaogu-backup.timer"
    echo "下一步：按 deploy/env.example 在服务器写 /etc/xiaogu/staging.env 和 /etc/xiaogu/prod.env（chmod 600），配置 nginx（deploy/nginx.conf），然后 deploy.sh staging。"
    ;;

  staging)
    echo "== 本机测试"
    (cd "$ROOT" && .venv/bin/python -m pytest -q -p no:warnings)
    echo "== 同步代码到测试环境"
    rsync -az --delete --rsync-path="sudo -u xiaogu rsync" \
      --exclude .git --exclude .venv --exclude __pycache__ --exclude 'web/data/' --exclude 'web/logs/' \
      --exclude dist --exclude evidence --exclude .claude --exclude 'deploy/*.env' \
      "$ROOT/" "$HOST:/opt/xiaogu/staging/"
    release="$(date +%Y%m%d-%H%M%S)-$(cd "$ROOT" && git rev-parse --short HEAD 2>/dev/null || echo nogit)"
    remote "echo $release | sudo -u xiaogu tee /opt/xiaogu/staging/RELEASE >/dev/null"
    install_env staging
    remote "sudo systemctl enable xiaogu@staging >/dev/null 2>&1; sudo systemctl restart xiaogu@staging"
    health staging 8102
    echo "测试环境已更新到 $release。到 https://staging.<域名> 手动走一遍：登录 → 对话 → 简历 → 模拟面试 → 后台。没问题再 deploy.sh prod。"
    ;;

  prod)
    staged="$(remote "cat /opt/xiaogu/staging/RELEASE 2>/dev/null || true")"
    [ -n "$staged" ] || { echo "测试环境还没有发布过，先 deploy.sh staging"; exit 1; }
    current="$(remote "cat /opt/xiaogu/prod/RELEASE 2>/dev/null || echo 无")"
    echo "生产当前：$current"
    echo "将发布：  $staged（测试环境里正在跑的这一版）"
    read -r -p "确认发布到生产？输入 yes：" answer
    [ "$answer" = "yes" ] || { echo "已取消"; exit 1; }
    remote "sudo -u xiaogu rsync -a --delete --exclude .venv /opt/xiaogu/staging/ /opt/xiaogu/prod/"
    install_env prod
    remote "sudo systemctl enable xiaogu@prod >/dev/null 2>&1; sudo systemctl restart xiaogu@prod"
    health prod 8101
    echo "生产已更新到 $staged。回滚：服务器上 /var/backups/xiaogu 有每日数据库备份；代码回滚 = 把上一版重新 deploy.sh staging 再 prod。"
    ;;

  *)
    sed -n '2,9p' "$0"; exit 1 ;;
esac
