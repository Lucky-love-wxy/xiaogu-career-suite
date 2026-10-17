#!/bin/bash
set -euo pipefail
install -d -m 700 /root/.ssh
touch /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
grep -Fqx 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIztQWfh78X0iy5FVesD3nCRZEafhQWmjndiL4uOeRrP xiaogu-launch-aliyun-20261006' /root/.ssh/authorized_keys || printf '%s\n' 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIztQWfh78X0iy5FVesD3nCRZEafhQWmjndiL4uOeRrP xiaogu-launch-aliyun-20261006' >> /root/.ssh/authorized_keys
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
id xiaogu
stat -c '%a %U %n' /etc/xiaogu /var/backups/xiaogu /opt/xiaogu/staging
python3 --version
printf 'XIAOGU_SSH_READY\n'
