import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
data = open(os.path.join(OUT, 'main.9182d5c6c2944413c6f0.js'), encoding='utf-8', errors='replace').read()

def ctx(token, width=1400, maxh=3):
    print(f'\n===== {token} =====')
    idxs = [m.start() for m in re.finditer(re.escape(token), data)]
    print(f'{len(idxs)} occurrences')
    for i in idxs[:maxh]:
        print(data[max(0, i-120):i+width].replace('\n', ' '))
        print('-' * 90)

for t in ['BASE_LOGIN_URL', 'BASE_URL_USR_MGMT', 'getClientWithHeader', 'postClient(', 'getClient(', 'environment[']:
    ctx(t)
