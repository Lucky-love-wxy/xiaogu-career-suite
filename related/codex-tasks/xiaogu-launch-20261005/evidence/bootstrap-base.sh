#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-venv sqlite3 rsync curl apache2-utils ca-certificates
id xiaogu >/dev/null 2>&1 || useradd --system --home /opt/xiaogu --shell /usr/sbin/nologin xiaogu
install -d -m 750 -o xiaogu -g xiaogu /opt/xiaogu/staging /opt/xiaogu/prod /var/lib/xiaogu/staging /var/lib/xiaogu/prod
install -d -m 700 /etc/xiaogu /var/backups/xiaogu
python3 --version
sqlite3 --version
printf 'XIAOGU_BASE_READY\n'
