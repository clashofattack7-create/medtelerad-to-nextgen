import urllib.request, re, os, ssl

BASE = 'https://nextgen.ehospital.gov.in'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
os.makedirs(OUT, exist_ok=True)
ctx = ssl.create_default_context()
UA = {'User-Agent': 'Mozilla/5.0'}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read()

srcs = []
for path in ['/ris/', '/ris']:
    try:
        idx = get(BASE + path).decode('utf-8', 'replace')
        print('=== ', path, ' === len=', len(idx))
        srcs = re.findall(r'<script[^>]+src="([^"]+)"', idx)
        for s in srcs:
            print('  script:', s)
        open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(idx)
        break
    except urllib.error.HTTPError as e:
        print(path, 'HTTP', e.code)
    except Exception as e:
        print(path, 'err', repr(e))

print('\n--- downloading bundles ---')
for s in srcs:
    if s.startswith('http'):
        url = s
    elif s.startswith('/'):
        url = BASE + s
    else:
        url = BASE + '/ris/' + s
    name = os.path.basename(url.split('?')[0])
    try:
        data = get(url)
        open(os.path.join(OUT, name), 'wb').write(data)
        print(f'{name}: {len(data)} bytes')
    except Exception as e:
        print(f'{name}: ERROR {e!r}')
