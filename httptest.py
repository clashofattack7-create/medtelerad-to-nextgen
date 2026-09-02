import ssl, socket, urllib.request, json, sys

# 1. library check
try:
    import requests
    print('requests version:', requests.__version__)
except ImportError:
    print('requests: NOT installed')

# 2. certificate info
host = 'nextgen.ehospital.gov.in'
print('\n--- cert info ---')
ctx_raw = ssl._create_unverified_context()
with socket.create_connection((host, 443), timeout=15) as sock:
    with ctx_raw.wrap_socket(sock, server_hostname=host) as ss:
        cert = ss.getpeercert(binary_form=False)
        print('subject:', cert.get('subject'))
        print('issuer :', cert.get('issuer'))
        print('notAfter:', cert.get('notAfter'))

# 3. validated GET (system CA store)
print('\n--- validated GET (default context) ---')
try:
    req = urllib.request.Request('https://' + host + '/adminHome', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        print('status:', r.status)
        print('final URL:', r.geturl())
        body = r.read()
        print('body length:', len(body))
        print('body head:', body[:300].decode('utf-8', 'replace').replace('\n', ' ')[:300])
except urllib.error.HTTPError as e:
    print('HTTPError', e.code, '| url:', e.geturl())
    print('body head:', e.read()[:300].decode('utf-8', 'replace').replace('\n', ' ')[:300])
except Exception as e:
    print('err:', repr(e))

# 4. unverified GET fallback
print('\n--- unverified GET (CERT_NONE) ---')
try:
    req = urllib.request.Request('https://' + host + '/adminHome', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=20, context=ctx_raw) as r:
        print('status:', r.status, '| final URL:', r.geturl())
        body = r.read()
        print('body length:', len(body))
        print('body head:', body[:300].decode('utf-8', 'replace').replace('\n', ' ')[:300])
except Exception as e:
    print('err:', repr(e))
