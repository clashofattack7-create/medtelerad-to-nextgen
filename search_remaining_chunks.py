import urllib.request, ssl, os, re
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
BASE = 'https://nextgen.ehospital.gov.in/ris/'
ctx = ssl.create_default_context()

chunks = {
    6: 'module-radiology-administration-test-vs-room-mapping-test_vs_room_mapping-module.ddbbb6af527ddeb0c251.js',
    7: 'module-rediology-information-system-image-capture-config-image-capture-config-module.98ad2fd72e01b49e7397.js',
    8: 'module-rediology-information-system-imaging_mis-imaging_mis-module.9107d2534d63bf253cbf.js',
    9: 'module-rediology-information-system-report-print-report_print-module.e7510f4b24c86b212e88.js',
}

for cid, fname in chunks.items():
    path = os.path.join(OUT, fname)
    if not os.path.exists(path):
        try:
            r = urllib.request.Request(BASE + fname, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
                open(path, 'wb').write(resp.read())
        except Exception as e:
            print(f'chunk {cid}: download ERR {e!r}')
            continue
    data = open(path, encoding='utf-8', errors='replace').read()
    print(f'\n=== chunk {cid} ({fname[:50]}...) {len(data)} bytes ===')
    for tok in ['cancel', 'delete', 'void', 'Cancel', 'Delete', 'Void']:
        idxs = [m.start() for m in re.finditer(re.escape(tok), data)]
        if idxs:
            for i in idxs[:2]:
                seg = data[max(0, i-200):i+500].replace('\n', ' ')
                if any(k in seg.lower() for k in ['order', 'report', 'service', 'status', 'v1/']):
                    print(f'  [{tok}] {seg[:400]}')
    # any v1 endpoints
    eps = set(re.findall(r'["\'](v1/[a-zA-Z0-9_\-/]+)["\']', data))
    if eps:
        print('  v1 endpoints:', sorted(eps))
