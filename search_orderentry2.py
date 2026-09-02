import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
data = open(os.path.join(OUT, 'main.1f4297bd0d1e0d82fe5a.js'), encoding='utf-8', errors='replace').read()

# find the payload object built before save_centralized_patient_service_order_entry
for anchor in ['objjjjjjjjjjjjjj', 'patient_scheme_id']:
    idxs = [m.start() for m in re.finditer(re.escape(anchor), data)]
    print(f'===== {anchor}: {len(idxs)} hits =====')
    for i in idxs[:2]:
        print(data[max(0, i-4000):i+600].replace('\n', ' '))
        print('\n' + '=' * 100 + '\n')
