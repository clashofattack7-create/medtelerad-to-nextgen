import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
data = open(os.path.join(OUT, 'main.9182d5c6c2944413c6f0.js'), encoding='utf-8', errors='replace').read()

print('=== loadChildren / module chunk names ===')
for m in re.finditer(r'loadChildren[:\s]*\(?[^)]*?["\']([^"\']+)["\']', data):
    print(' ', m.group(1))

print('\n=== strings with "cancel"/"cancell" (any) ===')
seen = set()
for m in re.finditer(r'["\']([^"\']*(?:cancel|cancell)[^"\']*)["\']', data, re.I):
    s = m.group(1)
    if s not in seen and len(s) < 120:
        seen.add(s)
        print(' ', s)
