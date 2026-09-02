import urllib.request, urllib.error, ssl, json

BASE = 'https://nextgen.ehospital.gov.in'
ctx = ssl.create_default_context()

def req(method, path, headers=None, data=None):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    if headers:
        h.update(headers)
    body = data.encode('utf-8') if isinstance(data, str) else data
    r = urllib.request.Request(BASE + path, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=30, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 'ERR', str(e).encode()

for path in ['/api/authentication/v1/pubkey',
             '/api/authentication/v1/pubkey/',
             '/api/authentication/v1/captcha_image']:
    st, b = req('GET', path)
    print(f'\nGET {path} -> {st}')
    print(b[:400].decode('utf-8', 'replace'))

# try POST login with empty body to see response shape
st, b = req('POST', '/api/authentication/v1/login', data='{}')
print(f'\nPOST /api/authentication/v1/login ({{}}) -> {st}')
print(b[:400].decode('utf-8', 'replace'))
