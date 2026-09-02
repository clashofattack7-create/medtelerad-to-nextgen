import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
ctx = ssl.create_default_context()

def call(method, url, headers=None, data=None):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
         'Authorization': f'Bearer {token}'}
    if headers:
        h.update(headers)
    body = json.dumps(data).encode() if data is not None else None
    if data is not None:
        h['Content-Type'] = 'application/json'
    r = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()
        except Exception:
            return e.code, b''

# 1. patient search by UHID
print('=== patient search (patientLastVisitSearch) for 202600XXXXX ===')
st, b = call('POST', 'https://nextgen.ehospital.gov.in/api/search/patient/patientLastVisitSearch/1',
             data={'SearchCri': 'UHID', 'health_facility_id': HF, 'pat_uhid': '202600XXXXX'})
print('status:', st)
txt = b.decode('utf-8', 'replace')
print(txt[:2000])

# 2. RIS service category list
print('\n=== RIS service_category list ===')
st, b = call('GET', 'https://nextgen.ehospital.gov.in/api/ris/api/ris/v1/service_category',
             headers={'healthFacilityId': HF})
print('status:', st)
print(b.decode('utf-8', 'replace')[:2000])
