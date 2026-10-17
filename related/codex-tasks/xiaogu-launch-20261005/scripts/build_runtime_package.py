#!/usr/bin/env python3
"""构建小谷测试环境白名单包，不包含本机数据库、日志、凭据或用户材料。
运行：python3 build_runtime_package.py SOURCE OUTPUT_DIRECTORY
输出：runtime.tar.gz、runtime-manifest.json；仅依赖 Python 标准库。
相同文件内容产生相同 release 标识，输出可重复覆盖，不修改来源。
"""
import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path

source, output = map(Path, sys.argv[1:])
files = set(source.glob('web/*.py')) | {source / 'web/requirements.txt'}
files |= set((source / 'web/static').glob('*'))
for subtree in ('skills/xiaogu-career-master/scripts', 'skills/xiaogu-career-master/references',
                'skills/xiaogu-career-suite/scripts', 'skills/xiaogu-career-suite/references',
                'database'):
    files |= {p for p in (source / subtree).rglob('*') if p.is_file() and p.suffix in ('.py', '.json', '.md')}
mock = source / 'examples/algorithm-engineer-mock'
files |= {mock / n for n in ('live_sources.json', 'jd.txt')}
files |= {p for p in (mock / 'responses').glob('*.json')}
files.add(source / 'deploy/xiaogu@.service')
rows = []
for p in sorted(files):
    if not p.is_file() or p.is_symlink():
        raise SystemExit(f'禁止缺失文件或符号链接：{p.relative_to(source)}')
    name = str(p.relative_to(source))
    if any(part in name.split('/') for part in ('__pycache__', 'logs', '.git', 'profile')) or p.suffix not in ('.py', '.txt', '.html', '.css', '.js', '.svg', '.json', '.md', '.service'):
        raise SystemExit(f'禁止包内文件：{name}')
    data = p.read_bytes()
    if re.search(rb'sk-[A-Za-z0-9_-]{24,}', data):
        raise SystemExit(f'可能含API key，停止打包：{name}')
    rows.append({'path': name, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
release = 'staging-' + hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()[:16]
output.mkdir(parents=True, exist_ok=True)
archive = output / 'runtime.tar.gz'
with tarfile.open(archive, 'w:gz') as tf:
    for row in rows:
        p = source / row['path']
        # 确保清单生成后来源没有发生并发变化。
        if hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            raise SystemExit('来源变化，停止打包')
        info = tf.gettarinfo(str(p), arcname=row['path'])
        info.uid = info.gid = 0
        info.uname = info.gname = ''
        info.mode = 0o644
        with p.open('rb') as f:
            tf.addfile(info, f)
manifest = {'release': release, 'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(), 'files': rows,
            'scope': 'localhost-only staging with mock model; no production publishing'}
(output / 'runtime-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'release': release, 'files': len(rows), 'bytes': archive.stat().st_size, 'sha256': manifest['archive_sha256']}, ensure_ascii=False))
