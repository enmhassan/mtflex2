import re
import os

BASE='.'
req='requirements.txt'

with open(req,'r',encoding='utf-8',errors='ignore') as f:
    pkgs=[line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]

py_files=[]
for root,dirs,files in os.walk(BASE):
    # skip virtualenv
    if '.venv' in root.split(os.sep):
        continue
    for fn in files:
        if fn.endswith('.py'):
            py_files.append(os.path.join(root,fn))

used=set()
for pkg in pkgs:
    name=pkg.lower()
    candidates={name, name.replace('-','_'), name.replace('-',''), name.split('-')[0]}
    # also try strip namespace like huggingface_hub -> huggingface
    if '_' in name:
        candidates.add(name.split('_')[0])
    pattern = re.compile(r"^\s*(?:from|import)\s+(%s)\b" % '|'.join(re.escape(c) for c in candidates))
    for py in py_files:
        try:
            with open(py,'r',encoding='utf-8',errors='ignore') as f:
                for line in f:
                    if pattern.search(line):
                        used.add(pkg)
                        raise StopIteration
        except StopIteration:
            continue

unused=[p for p in pkgs if p not in used]
print('Used packages (%d):' % len(used))
for u in sorted(used):
    print('  ',u)
print('\nUnused packages (%d):' % len(unused))
for u in sorted(unused):
    print('  ',u)
