import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
files = [
    'module-rediology-information-system-scheduling-scheduling-module.5fe5446219a67c95f59f.js',
    'module-rediology-information-system-report_creation-report_creation-module.8bd665dfee9f85fab59c.js',
    'module-rediology-information-system-report-verification-report-verification-module.6a33e295c019ae6aa307.js',
]

# find all v1/... endpoint strings
allpaths = set()
for f in files:
    data = open(os.path.join(OUT, f), encoding='utf-8', errors='replace').read()
    for m in re.finditer(r'["\'](v1/[a-zA-Z0-9_\-/]+)["\']', data):
        allpaths.add(m.group(1))

print('v1 endpoints in chunks:')
for p in sorted(allpaths):
    print(' ', p)

# search cancel/delete context
for f in files:
    data = open(os.path.join(OUT, f), encoding='utf-8', errors='replace').read()
    for tok in ['cancel', 'delete', 'void', 'Cancel', 'Delete']:
        idxs = [m.start() for m in re.finditer(re.escape(tok), data)]
        if idxs:
            for i in idxs[:2]:
                seg = data[max(0, i-250):i+600]
                if '/v1/' in seg or 'cancel' in seg.lower() or 'delete' in seg.lower():
                    print(f'\n[{f}] {tok} @ {i}:')
                    print(seg.replace('\n', ' '))
