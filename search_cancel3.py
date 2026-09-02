import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
data = open(os.path.join(OUT, 'main.1f4297bd0d1e0d82fe5a.js'), encoding='utf-8', errors='replace').read()

# find URL-like strings containing cancel/delete/void/revoke/unverify
pats = set()
for m in re.finditer(r'["\']([^"\']*(?:cancel|delete|void|revoke|unverify|un_verify|undo)[^"\']*)["\']', data, re.I):
    s = m.group(1)
    if ('/' in s or 'api' in s.lower()) and len(s) < 120:
        pats.add(s)
print('URL-like cancel/delete/void strings:')
for p in sorted(pats):
    print(' ', p)

# also look for the centralized order entry module endpoints
print('\ncentralized order entry endpoints:')
for m in re.finditer(r'["\'](v1/[a-zA-Z0-9_\-/]+)["\']', data):
    s = m.group(1)
    if 'centralized' in s or 'order' in s or 'cancel' in s:
        print(' ', s)
