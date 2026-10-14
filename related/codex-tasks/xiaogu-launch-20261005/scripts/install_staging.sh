#!/bin/bash
# 仅为小谷新服务器安装 localhost/mock staging，重复执行只接受同一发布包。
# 用法：bash install_staging.sh ARCHIVE SHA256 RELEASE；需root、Python3和网络。
set -euo pipefail
umask 077
archive="$1"; expected="$2"; release="$3"; prior="${4:-}"
printf '%s  %s\n' "$expected" "$archive" | sha256sum -c -
cd /opt/xiaogu/staging
if [ -e web/app.py ] && [ "$(cat .xiaogu-stage-candidate 2>/dev/null || true)" != "$release" ]; then
    if [ -z "$prior" ] || [ "$(cat VERIFIED_RELEASE 2>/dev/null || true)" != "$prior" ] || [ "$(cat .xiaogu-stage-candidate 2>/dev/null || true)" != "$prior" ]; then
        echo '测试目录已有未经授权的发布，停止覆盖'; exit 1
    fi
    backup="/var/backups/xiaogu/staging-pre-$release.db"
    sqlite3 /var/lib/xiaogu/staging/xiaogu.db ".backup $backup"
    test "$(sqlite3 "$backup" 'PRAGMA integrity_check;')" = ok
    chmod 600 "$backup"
    systemctl stop xiaogu@staging
fi
printf '%s\n' "$release" > .xiaogu-stage-candidate
tar -xzf "$archive" --no-same-owner --no-same-permissions
chown -R xiaogu:xiaogu /opt/xiaogu/staging
chmod 750 /opt/xiaogu/staging
runuser -u xiaogu -- python3 -m venv /opt/xiaogu/staging/.venv
runuser -u xiaogu -- /opt/xiaogu/staging/.venv/bin/pip install --disable-pip-version-check -q -i https://mirrors.aliyun.com/pypi/simple/ -r /opt/xiaogu/staging/web/requirements.txt
python3 - <<'PY'
from pathlib import Path
import secrets, os
p=Path('/etc/xiaogu/staging.env')
if not p.exists():
    value='\n'.join(['XIAOGU_ENV=staging','PORT=8102','XIAOGU_PROVIDER=mock',
        'XIAOGU_DB=/var/lib/xiaogu/staging/xiaogu.db','XIAOGU_LOGIN_SENDER=console',
        'XIAOGU_SECRET='+secrets.token_hex(32),'XIAOGU_ADMIN_TOKEN='+secrets.token_urlsafe(32)])+'\n'
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:f.write(value)
p.chmod(0o600)
PY
unit=/etc/systemd/system/xiaogu@.service
if [ -e "$unit" ] && ! cmp -s deploy/xiaogu@.service "$unit"; then
    echo '已有不同的同名服务单元，停止覆盖'; exit 1
fi
install -m 644 deploy/xiaogu@.service "$unit"
systemctl daemon-reload
systemctl enable xiaogu@staging
systemctl restart xiaogu@staging
python3 - <<'PY'
import json, time, urllib.request
for attempt in range(30):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8102/api/meta',timeout=2) as r:
            m=json.load(r)
        assert m['env']=='staging' and m['provider']=='mock',m
        print(json.dumps(m,ensure_ascii=False))
        break
    except Exception:
        if attempt==29:raise
        time.sleep(1)
PY
printf '%s\n' "$release" > VERIFIED_RELEASE
systemctl is-active xiaogu@staging
ss -ltnp | grep ':8102 '
printf 'XIAOGU_STAGING_READY %s\n' "$release"
