import urllib.request, json, ssl

# crypto library availability (for RSA password encryption)
for mod in ['cryptography', 'Crypto', 'rsa', 'Cryptodome']:
    try:
        __import__(mod)
        print(f'{mod}: AVAILABLE')
    except ImportError:
        print(f'{mod}: NOT available')

BASE = 'https://nextgen.ehospital.gov.in'
ctx = ssl.create_default_context()

def get(url, headers=None):
    h = {'User-Agent': 'Mozilla/5.0'}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.status, dict(r.headers), r.read()

print('\n--- pubkey ---')
st, hd, body = get(BASE + '/api/authentication/v1/pubkey')
print('status:', st, '| content-type:', hd.get('Content-Type'))
txt = body.decode('utf-8', 'replace')
print(txt[:600])

print('\n--- captcha_image (empty id/captchaId) ---')
st, hd, body = get(BASE + '/api/authentication/v1/captcha_image', {'id': '', 'captchaId': ''})
print('status:', st, '| content-type:', hd.get('Content-Type'))
txt = body.decode('utf-8', 'replace')
print(txt[:200])
try:
    j = json.loads(txt)
    print('keys:', list(j.keys()))
    for k in j:
        v = j[k]
        print(f'  {k}: {type(v).__name__} len={len(v) if isinstance(v,str) else "n/a"}')
except Exception as e:
    print('not json:', e)
