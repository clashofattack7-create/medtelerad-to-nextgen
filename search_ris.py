import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
data = open(os.path.join(OUT, 'main.1f4297bd0d1e0d82fe5a.js'), encoding='utf-8', errors='replace').read()
print('main.js chars:', len(data))

# extract API path-like string literals
paths = set()
for m in re.finditer(r'["\'](/[a-zA-Z0-9_\-./]+(?:/[a-zA-Z0-9_\-./]+)+)["\']', data):
    s = m.group(1)
    if any(k in s.lower() for k in ('api', 'upload', 'report', 'ris', 'order', 'study', 'file', 'document', 'attach', 'report', 'radiology')):
        if len(s) < 120:
            paths.add(s)
print(f'\n--- API path literals ({len(paths)}) ---')
for p in sorted(paths):
    print(p)
