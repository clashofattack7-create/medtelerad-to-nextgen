import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
RIS = 'https://nextgen.ehospital.gov.in/api/ris/api/ris'
ctx = ssl.create_default_context()

def get(url, headers):
    r = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

h = {
    'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
    'Authorization': f'Bearer {token}',
    'healthFacilityId': HF,
    'OrderDateStart': '31/08/2026', 'OrderDateEnd': '01/09/2026',
    'ProcedureCategoryCode': '', 'ProcedureId': '',
    'RegistrationId': '', 'StudyNumber': '',
    'serviceStatus': '', 'RoomId': '',
}
st, b = get(RIS + '/v1/ris_patient_search', h)
data = json.loads(b)
open(os.path.join(BASE_DIR, 'ris_search_full.json'), 'w').write(json.dumps(data, indent=2))
rows = data.get('result') or []
print('total orders:', len(rows))
print(f'{"name":22s} {"registration_id":16s} {"study_no":8s} {"status":18s} {"service"}')
print('-' * 90)
for r in rows:
    print(f'{r.get("patient_name","")[:22]:22s} {r.get("registration_id",""):16s} {r.get("study_number",""):8s} {r.get("service_status",""):18s} {r.get("service_name","")[:30]}')
