import re, os
BASE = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(BASE, 'mt_after_login.html'), encoding='utf-8', errors='replace').read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S | re.I)
alljs = '\n'.join(scripts)
print('num script blocks:', len(scripts), '| total js chars:', len(alljs))

def show(fn, width=1800, maxh=4):
    print(f'\n===== {fn} =====')
    hits = [m.start() for m in re.finditer(re.escape(fn), alljs)]
    seen = set()
    n = 0
    for i in hits:
        seg = alljs[max(0, i-120):i+width]
        key = seg[:60]
        if key in seen:
            continue
        seen.add(key)
        print(seg)
        print('-' * 70)
        n += 1
        if n >= maxh:
            break

for fn in ['lnkRpt', 'fetchXML', 'function Report', 'lnkVwr', 'RadVwr', 'btnZipDownload']:
    show(fn)

print('\n===== URLs mentioning ashx/zip/pdf/report/download =====')
for m in re.finditer(r'["\'](/[^"\']*(?:ashx|zip|pdf|report|download|FinalizedReport)[^"\']*)["\']', alljs, re.I):
    print(m.group(1))
