import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
data = open(os.path.join(OUT, 'main.9182d5c6c2944413c6f0.js'), encoding='utf-8', errors='replace').read()

def ctx(token, width=1300, maxh=4):
    print(f'\n===== {token} =====')
    idxs = [m.start() for m in re.finditer(re.escape(token), data)]
    print(f'{len(idxs)} occurrences')
    for i in idxs[:maxh]:
        print(data[max(0, i-100):i+width].replace('\n', ' '))
        print('-' * 80)

for t in ['CAPTCHA_DISABLE', 'decryptUsingAES256', 'encryptUsingAES256', 'setPublicKey']:
    ctx(t)
