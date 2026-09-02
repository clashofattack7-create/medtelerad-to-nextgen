import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
ctx = ssl.create_default_context()

def probe(method, path):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    r = urllib.request.Request('https://nextgen.ehospital.gov.in' + path, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30, context=ctx) as resp:
            return resp.status, resp.read()[:200]
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()[:200]
        except Exception:
            return e.code, b''
    except Exception as e:
        return 'ERR', str(e).encode()

candidates = [
    '/api/ris/api/ris/v1/cancel_order',
    '/api/ris/api/ris/v1/cancel_report',
    '/api/ris/api/ris/v1/delete_report',
    '/api/ris/api/ris/v1/cancel_service_order',
    '/api/ris/api/ris/v1/cancel_service_confirmation',
    '/api/centralized_patient/v1/cancel_order',
    '/api/centralized_patient/v1/cancel_service_order',
    '/api/centralized_patient/v1/centralized_patient_service_order_cancel',
    '/api/centralized_patient/v1/cancel_centralized_patient_service_order',
    '/api/ris/api/ris/v1/ris_cancel',
]
for p in candidates:
    st, b = probe('GET', p)
    print(f'GET {p} -> {st} {b.decode("utf-8","replace")[:80]}')
