import urllib.request, ssl, os, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
BASE = 'https://nextgen.ehospital.gov.in/ris/'
ctx = ssl.create_default_context()

chunks = {
    11: 'module-rediology-information-system-report_creation-report_creation-module.8bd665dfee9f85fab59c.js',
    10: 'module-rediology-information-system-report-verification-report-verification-module.6a33e295c019ae6aa307.js',
}

def fetch(url):
    r = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
        return resp.read()

for cid, fname in chunks.items():
    url = BASE + fname
    try:
        data = fetch(url)
        open(os.path.join(OUT, fname), 'wb').write(data)
        print(f'chunk {cid}: saved {fname} ({len(data)} bytes)')
    except Exception as e:
        print(f'chunk {cid}: ERR {e!r}')
