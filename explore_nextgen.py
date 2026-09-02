import urllib.request, re, os, ssl

BASE = 'https://nextgen.ehospital.gov.in'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
os.makedirs(OUT, exist_ok=True)
ctx = ssl.create_default_context()
UA = {'User-Agent': 'Mozilla/5.0'}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        return r.read()

idx = get(BASE + '/adminHome').decode('utf-8', 'replace')
print('--- script srcs in index ---')
srcs = re.findall(r'<script[^>]+src="([^"]+)"', idx)
for s in srcs:
    print(s)

print('\n--- downloading bundles ---')
for s in srcs:
    url = BASE + s if s.startswith('/') else (s if s.startswith('http') else BASE + '/' + s)
    name = os.path.basename(url.split('?')[0])
    try:
        data = get(url)
        with open(os.path.join(OUT, name), 'wb') as f:
            f.write(data)
        print(f'{name}: {len(data)} bytes')
    except Exception as e:
        print(f'{name}: ERROR {e!r}')
