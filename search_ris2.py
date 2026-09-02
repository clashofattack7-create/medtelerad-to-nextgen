import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
data = open(os.path.join(OUT, 'main.1f4297bd0d1e0d82fe5a.js'), encoding='utf-8', errors='replace').read()

def ctx(token, width=1100, maxh=4):
    print(f'\n===== {token} =====')
    idxs = [m.start() for m in re.finditer(re.escape(token), data)]
    print(f'{len(idxs)} occurrences')
    seen = set(); n = 0
    for i in idxs:
        seg = data[max(0, i-200):i+width]
        key = seg[:70]
        if key in seen:
            continue
        seen.add(key)
        print(seg.replace('\n', ' '))
        print('-' * 80)
        n += 1
        if n >= maxh:
            break

for t in ['report_creation', 'FormData', 'multipart', 'report_update', 'ris_patient_search', 'report_template']:
    ctx(t)
