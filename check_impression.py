import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
ctx = ssl.create_default_context()

def call(method, url, headers=None):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    h.update(headers or {})
    r = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

st, b = call('GET', 'https://nextgen.ehospital.gov.in/api/ris/api/ris/v1/report', {
    'serviceId': '1301000538', 'orderId': '1d8acd4d-7b11-4b36-8a04-12f29243d929',
    'healthFacilityId': HF, 'serviceStatus': 'REPORT_VERIFIED', 'registrationId': '202600XXXXX'})
d = json.loads(b)
r = d['result'][0]
print('report_title:', repr(r.get('report_title')))
print('report_impression:', repr(r.get('report_impression')))
print('report_prepared_by:', repr(r.get('report_prepared_by')))
print('report_verified_by:', repr(r.get('report_verified_by')))
print('report_description (len %d):' % len(r.get('report_description') or ''))
print((r.get('report_description') or '')[:500])
