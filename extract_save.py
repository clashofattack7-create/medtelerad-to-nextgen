import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
fn = 'module-rediology-information-system-report_creation-report_creation-module.8bd665dfee9f85fab59c.js'
data = open(os.path.join(OUT, fn), encoding='utf-8', errors='replace').read()

# print the full save() method and the button handlers
for m in re.finditer(r'save\(t\)', data):
    i = m.start()
    print('=== save(t) at', i, '===')
    print(data[max(0, i-100):i+3000].replace('\n', ' '))
    print('\n')
