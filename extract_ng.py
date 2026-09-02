import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
data = open(os.path.join(OUT, 'main.9182d5c6c2944413c6f0.js'), encoding='utf-8', errors='replace').read()

def ctx(token, width=900, max_hits=4):
    print(f'\n===== {token} =====')
    idxs = [m.start() for m in re.finditer(re.escape(token), data)]
    print(f'{len(idxs)} occurrences (showing up to {max_hits})')
    for i in idxs[:max_hits]:
        s = max(0, i - width // 3)
        e = min(len(data), i + width)
        print(data[s:e].replace('\n', ' '))
        print('-' * 90)

for t in ['v1/login', 'getPublicKey', 'getCaptchaImage', '/api/authentication', 'captcha', 'encryptText', 'public_key']:
    ctx(t)
