import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
data = open(os.path.join(OUT, 'main.9182d5c6c2944413c6f0.js'), encoding='utf-8', errors='replace').read()

def ctx(token, width=700, maxh=4):
    print(f'\n===== {token} =====')
    idxs = [m.start() for m in re.finditer(re.escape(token), data, re.I)]
    print(f'{len(idxs)} occurrences')
    seen = set(); n = 0
    for i in idxs:
        seg = data[max(0, i-150):i+width]
        key = seg[:60]
        if key in seen:
            continue
        seen.add(key)
        print(seg.replace('\n', ' '))
        print('-' * 70)
        n += 1
        if n >= maxh:
            break

for t in ['multipart', 'upload', 'receipt', 'mrd']:
    ctx(t)
