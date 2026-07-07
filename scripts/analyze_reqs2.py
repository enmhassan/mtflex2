import ast, os, subprocess, sys

# collect top-level imported module names from .py files
imports=set()
for root,dirs,files in os.walk('.'):
    if '.venv' in root.split(os.sep):
        continue
    for fn in files:
        if fn.endswith('.py'):
            path=os.path.join(root,fn)
            try:
                with open(path,'r',encoding='utf-8',errors='ignore') as f:
                    tree=ast.parse(f.read(), filename=path)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for n in node.names:
                                imports.add(n.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split('.')[0])
            except Exception:
                pass

# get pip freeze packages
proc=subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True)
pkgs_raw=proc.stdout.splitlines()
pkgs=[line.strip() for line in pkgs_raw if line.strip()]

used=[]
unused=[]
for pkg in pkgs:
    name=pkg.split('==')[0]
    cand=set()
    low=name.lower()
    cand.add(low)
    cand.add(low.replace('-','_'))
    cand.add(low.replace('-',''))
    cand.add(low.split('-')[0])
    cand.add(low.split('_')[0])

    # also add some common mappings
    if low=='python-dateutil': cand.add('dateutil')
    if low=='pillow': cand.add('PIL')

    if any(c in imports for c in cand):
        used.append(pkg)
    else:
        unused.append(pkg)

print('Detected imports (sample 50):', list(sorted(imports))[:50])
print('\nUsed packages (%d):' % len(used))
for u in sorted(used): print('  ',u)
print('\nUnused packages (%d):' % len(unused))
for u in sorted(unused): print('  ',u)
