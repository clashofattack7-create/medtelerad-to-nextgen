import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
fn = 'module-rediology-information-system-report_creation-report_creation-module.8bd665dfee9f85fab59c.js'
data = open(os.path.join(OUT, fn), encoding='utf-8', errors='replace').read()

for tok in ['this.Data', 'finding_ai', 'Data=']:
    idxs = [m.start() for m in re.finditer(re.escape(tok), data)]
    print(f'===== {tok}: {len(idxs)} hits =====')
    for i in idxs[:4]:
        print(data[max(0, i-200):i+700].replace('\n', ' '))
        print('\n' + '-' * 85 + '\n')
