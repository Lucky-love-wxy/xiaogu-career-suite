#!/usr/bin/env python3
from pathlib import Path
import shutil
import zipfile
root=Path(__file__).resolve().parents[1]
out=root/'dist'/'xiaogu-career-suite-v2.zip'
out.parent.mkdir(exist_ok=True)
release_roots = {
    '_xiaogu-runtime', 'database', 'docs', 'examples', 'packages',
    'scripts', 'skills', 'tests',
}
release_files = {'README.md', 'LICENSE'}

# Keep standalone lookup Skills self-contained while the repository database
# remains the canonical editable source.
reality_refs = root / 'skills' / 'xiaogu-job-reality' / 'references'
for name in ('occupations.json', 'taxonomy.json'):
    shutil.copy2(root / 'database' / name, reality_refs / name)
suite_refs = root / 'skills' / 'xiaogu-career-suite' / 'references'
for name in ('jargon.json', 'occupations.json', 'taxonomy.json'):
    shutil.copy2(root / 'database' / name, suite_refs / name)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix == '.pyc':
            continue
        relative = p.relative_to(root)
        if relative.as_posix() in release_files or relative.parts[0] in release_roots:
            z.write(p, relative)
print(out)
