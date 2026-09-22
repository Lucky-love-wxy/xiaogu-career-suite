#!/usr/bin/env python3
from pathlib import Path
import tarfile, zipfile
root=Path(__file__).resolve().parents[1]
out=root/'dist'/'xiaogu-career-suite-v1.zip'
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        if p.is_file() and '.git' not in p.parts and 'dist' not in p.parts and '__pycache__' not in p.parts:
            z.write(p,p.relative_to(root))
print(out)
