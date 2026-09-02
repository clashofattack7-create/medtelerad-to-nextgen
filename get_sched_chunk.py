import urllib.request, ssl, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
BASE = 'https://nextgen.ehospital.gov.in/ris/'
ctx = ssl.create_default_context()
fname = 'module-rediology-information-system-scheduling-scheduling-module.5fe5446219a67c95f59f.js'
r = urllib.request.Request(BASE + fname, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
    data = resp.read()
open(os.path.join(OUT, fname), 'wb').write(data)
print('saved', fname, len(data), 'bytes')
