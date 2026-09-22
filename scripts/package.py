#!/usr/bin/env python3
from pathlib import Path
import shutil
import zipfile
root=Path(__file__).resolve().parents[1]
out=root/'dist'/'xiaogu-career-suite-v1.zip'
out.parent.mkdir(exist_ok=True)

# Keep the standalone xiaogu-job-reality Skill self-contained while the
# repository database remains the canonical editable source.
skill_refs = root / 'skills' / 'xiaogu-job-reality' / 'references'
for name in ('occupations.json', 'taxonomy.json'):
    shutil.copy2(root / 'database' / name, skill_refs / name)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        if p.is_file() and '.git' not in p.parts and 'dist' not in p.parts and '__pycache__' not in p.parts:
            z.write(p,p.relative_to(root))
print(out)
