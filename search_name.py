import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
data = open(os.path.join(OUT, 'main.1f4297bd0d1e0d82fe5a.js'), encoding='utf-8', errors='replace').read()

for tok in ['SearchCri', 'getPatientList(', 'getPatientLists(', 'pat_name', 'patientName', 'NameSearch']:
    idxs = [m.start() for m in re.finditer(re.escape(tok), data)]
    print(f'===== {tok}: {len(idxs)} hits =====')
    for i in idxs[:3]:
        print(data[max(0, i-350):i+800].replace('\n', ' '))
        print('\n' + '-' * 90 + '\n')
