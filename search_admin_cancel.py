import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
data = open(os.path.join(OUT, 'main.9182d5c6c2944413c6f0.js'), encoding='utf-8', errors='replace').read()

pats = set()
for m in re.finditer(r'["\']([^"\']*(?:cancel|delete|void|revoke)[^"\']*)["\']', data, re.I):
    s = m.group(1)
    if ('v1/' in s or 'api' in s.lower() or s.startswith('/')) and len(s) < 100:
        pats.add(s)
print('admin app cancel/delete/void URL strings:')
for p in sorted(pats):
    print(' ', p)
