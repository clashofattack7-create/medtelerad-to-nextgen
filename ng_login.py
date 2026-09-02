import urllib.request, urllib.error, json, ssl, os, base64
import ng_crypto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(BASE_DIR, 'config.json'), encoding='utf-8'))
BASE = cfg['nextgen']['base']
USER = cfg['nextgen']['user']
PASS = cfg['nextgen']['pass']

ctx = ssl.create_default_context()

def req(method, path, headers=None, data=None):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    if headers:
        h.update(headers)
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
        h['Content-Type'] = 'application/json'
    r = urllib.request.Request(BASE + path, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=40, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

# 1. pubkey
st, b = req('GET', '/api/authentication/v1/pubkey')
pub = json.loads(b)
pk = pub['result']['public_key']
print('pubkey b64 len:', len(pk))
n, e = ng_crypto.parse_rsa_public_key(base64.b64decode(pk))
print('RSA n bits:', n.bit_length(), '| e:', e)

# 2. encrypt password
enc_pw = ng_crypto.rsa_encrypt_pkcs1_v15(pk, PASS.encode('utf-8'))
print('encrypted password b64 len:', len(enc_pw))

# 3. captcha
st, b = req('GET', '/api/authentication/v1/captcha_image', {'id': '', 'captchaId': ''})
cap = json.loads(b)
print('captcha id:', cap['id'], '| captchaId:', cap['captchaId'], '| img bytes(b64):', len(cap['captchaImage']))

# 4. login (try dummy captcha first to see if captcha is enforced)
for cap_val in ['AAAAAA', '']:
    payload = {
        'user_id': USER,
        'password': enc_pw,
        'captcha_value': cap_val,
        'id': cap['id'],
        'captcha_id': cap['captchaId'],
    }
    st, b = req('POST', '/api/authentication/v1/login', data=payload)
    print(f'\nlogin (captcha={cap_val!r}) -> {st}')
    txt = b.decode('utf-8', 'replace')
    print(txt[:800])
