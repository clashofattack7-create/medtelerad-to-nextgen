import urllib.request, json, ssl, base64, os

BASE = 'https://nextgen.ehospital.gov.in'
ctx = ssl.create_default_context()
r = urllib.request.Request(BASE + '/api/authentication/v1/captcha_image',
                           headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
                                    'id': '', 'captchaId': ''})
with urllib.request.urlopen(r, timeout=30, context=ctx) as resp:
    cap = json.loads(resp.read())

img = base64.b64decode(cap['captchaImage'])
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'captcha.jpg')
open(out, 'wb').write(img)
print('saved', out, '|', len(img), 'bytes')
print('id:', cap['id'])
print('captchaId:', cap['captchaId'])
