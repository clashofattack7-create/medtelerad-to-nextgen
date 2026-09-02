import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
fn = 'module-rediology-information-system-report-verification-report-verification-module.6a33e295c019ae6aa307.js'
data = open(os.path.join(OUT, fn), encoding='utf-8', errors='replace').read()
print('chunk bytes:', len(data))

def ctx(token, width=1200, maxh=4):
    print(f'\n===== {token} =====')
    idxs = [m.start() for m in re.finditer(re.escape(token), data, re.I)]
    print(f'{len(idxs)} occurrences')
    seen = set(); n = 0
    for i in idxs:
        seg = data[max(0, i-250):i+width]
        key = seg[:70]
        if key in seen:
            continue
        seen.add(key)
        print(seg.replace('\n', ' '))
        print('-' * 85)
        n += 1
        if n >= maxh:
            break

for t in ['fb.group', 'report_verification', 'ReportVerification', 'verified_report', 'report_verified_by', 'is_verify', 'verification']:
    ctx(t)
