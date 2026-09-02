import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
data = open(os.path.join(OUT, 'main.9182d5c6c2944413c6f0.js'), encoding='utf-8', errors='replace').read()

for tok in ['SearchCri', 'searchPatient', 'patientSearch', 'search_criteria', 'searchCriteria']:
    idxs = [m.start() for m in re.finditer(re.escape(tok), data, re.I)]
    print(f'===== {tok}: {len(idxs)} hits =====')
    for i in idxs[:2]:
        print(data[max(0, i-300):i+900].replace('\n', ' '))
        print('\n' + '-' * 90 + '\n')
