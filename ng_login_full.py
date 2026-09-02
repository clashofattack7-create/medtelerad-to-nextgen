import urllib.request, urllib.error, json, ssl, os, base64, io, subprocess, time
from collections import Counter
from PIL import Image

import ng_crypto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(BASE_DIR, 'config.json'), encoding='utf-8'))
BASE = cfg['nextgen']['base']
USER = cfg['nextgen']['user']
PASS = cfg['nextgen']['pass']
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TMP = os.path.join(BASE_DIR, '.captcha_tmp')
os.makedirs(TMP, exist_ok=True)

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

def run_tess(png_path, psm):
    out = png_path + '.out'
    subprocess.run([TESS, png_path, out, '--psm', str(psm),
                    '-c', 'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        with open(out + '.txt', encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return ''

def ocr_captcha(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    w, h = img.size
    votes = Counter()
    p = os.path.join(TMP, 'c.png')
    for scale in (2, 3, 4):
        big = img.resize((w * scale, h * scale), Image.LANCZOS).convert('L')
        for thr in (None, 120, 150, 180):
            v = big if thr is None else big.point(lambda x: 255 if x > thr else 0)
            v.save(p)
            for psm in (7, 8, 13):
                t = run_tess(p, psm).strip()
                # keep alnum-only, 6 chars
                t = ''.join(ch for ch in t if ch.isalnum())
                if len(t) == 6:
                    votes[t] += 1
    if votes:
        return votes.most_common(1)[0][0], dict(votes)
    return '', {}

# fetch pubkey once, encrypt password once
st, b = req('GET', '/api/authentication/v1/pubkey')
pubkey_b64 = json.loads(b)['result']['public_key']
enc_pw = ng_crypto.rsa_encrypt_pkcs1_v15(pubkey_b64, PASS.encode('utf-8'))
aes_key = pubkey_b64[:16].encode('utf-8')
print('pubkey ok, encrypted password ready')

MAX_ATTEMPTS = 15
for attempt in range(1, MAX_ATTEMPTS + 1):
    st, b = req('GET', '/api/authentication/v1/captcha_image', {'id': '', 'captchaId': ''})
    cap = json.loads(b)
    img_bytes = base64.b64decode(cap['captchaImage'])
    guess, votes = ocr_captcha(img_bytes)
    print(f'[attempt {attempt}] captcha id={cap["id"]} OCR={guess!r} votes={votes}')

    payload = {
        'user_id': USER,
        'password': enc_pw,
        'captcha_value': guess,
        'id': cap['id'],
        'captcha_id': cap['captchaId'],
    }
    st, b = req('POST', '/api/authentication/v1/login', data=payload)
    resp = json.loads(b)
    msg = resp.get('metadata', {}).get('message', '')
    code = resp.get('metadata', {}).get('code', '')
    result = resp.get('result')
    print(f'   -> code={code} msg={msg!r} result={None if result is None else "PRESENT"}')

    if result:
        try:
            plain = ng_crypto.aes128_ecb_decrypt(aes_key, base64.b64decode(result))
            data = json.loads(plain)
            print('LOGIN SUCCESS')
            with open(os.path.join(BASE_DIR, 'nextgen_session.json'), 'w') as f:
                json.dump(data, f, indent=2)
            print('saved nextgen_session.json')
            print('keys:', list(data.keys()))
            print('access_token head:', (data.get('access_token') or '')[:40])
            break
        except Exception as e:
            print('   decrypt error:', repr(e))
    else:
        if 'captcha' in msg.lower():
            continue
        else:
            print('   unexpected error, stopping.')
            break
    time.sleep(0.3)
else:
    print('FAILED: could not solve captcha within', MAX_ATTEMPTS, 'attempts')
