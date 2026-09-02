import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
RIS = 'https://nextgen.ehospital.gov.in/api/ris/api/ris'
ctx = ssl.create_default_context()

# load the saved search results to find a verified order for PATIENT_F 
full = json.load(open(os.path.join(BASE_DIR, 'ris_search_full.json')))
rows = full.get('result') or []
target = None
for r in rows:
    if r.get('registration_id') == '202600UHID_B' and r.get('service_status') == 'REPORT_VERIFIED':
        target = r
        break
if not target:
    # fallback: first REPORT_VERIFIED row
    target = next((r for r in rows if r.get('service_status') == 'REPORT_VERIFIED'), rows[0])

print('target order:')
for k in ['registration_id', 'patient_name', 'order_id', 'service_id', 'study_number', 'service_status', 'service_name', 'report_creation_date', 'report_verification_date']:
    print(f'  {k}: {target.get(k)}')

def get(url, headers):
    r = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 'ERR', str(e).encode()

h = {
    'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
    'Authorization': f'Bearer {token}',
    'serviceId': str(target['service_id']),
    'orderId': str(target['order_id']),
    'healthFacilityId': HF,
    'serviceStatus': str(target['service_status']),
    'registrationId': str(target['registration_id']),
}
st, b = get(RIS + '/v1/report', h)
print('\nGET /v1/report -> status:', st, '| bytes:', len(b))
open(os.path.join(BASE_DIR, 'sample_ris_report.json'), 'wb').write(b)
txt = b.decode('utf-8', 'replace')
print(txt[:4000])
