import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')

# 1. look for lazy chunk references in main.js
main = open(os.path.join(OUT, 'main.1f4297bd0d1e0d82fe5a.js'), encoding='utf-8', errors='replace').read()
print('--- lazy chunk hints in main.js ---')
for m in re.finditer(r'["\']([A-Za-z0-9._-]+\.\d+[a-f0-9]+\.js)["\']', main):
    print(m.group(1))
# look for loadChildren / import(
print('\n--- loadChildren/import hits ---')
for kw in ['loadChildren', 'import(', 'e.import']:
    hits = [m.start() for m in re.finditer(re.escape(kw), main)]
    print(f'{kw}: {len(hits)}')

# 2. look at runtime.js for chunk map
runtime = open(os.path.join(OUT, 'runtime.00f768e16c5eec97da6e.js'), encoding='utf-8', errors='replace').read()
print('\n--- runtime.js (chunk config) ---')
print(runtime[:1500])
