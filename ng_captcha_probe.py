import urllib.request, json, ssl

BASE = 'https://nextgen.ehospital.gov.in'
ctx = ssl.create_default_context()

def get(path, headers=None):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    if headers:
        h.update(headers)
    r = urllib.request.Request(BASE + path, headers=h)
    with urllib.request.urlopen(r, timeout=30, context=ctx) as resp:
        return json.loads(resp.read().decode('utf-8'))

pub = get('/api/authentication/v1/pubkey')
pk = pub['result']['public_key']
print('pubkey length:', len(pk))
print('pubkey head (base64):', pk[:60])

cap = get('/api/authentication/v1/captcha_image', {'id': '', 'captchaId': ''})
print('\ncaptcha keys:', list(cap.keys()))
for k in cap:
    v = cap[k]
    if k == 'captchaImage':
        print(f'{k}: base64 len={len(v)}, first 24={v[:24]}')
    else:
        print(f'{k}: {v!r}')
