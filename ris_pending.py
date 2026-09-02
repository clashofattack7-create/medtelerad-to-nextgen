import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
RIS = 'https://nextgen.ehospital.gov.in/api/ris/api/ris'
ctx = ssl.create_default_context()

def search(over):
    h = {
        'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'healthFacilityId': HF,
        'OrderDateStart': '30/08/2026', 'OrderDateEnd': '01/09/2026',
        'ProcedureCategoryCode': '', 'ProcedureId': '',
        'RegistrationId': '', 'StudyNumber': '',
        'serviceStatus': 'CONFIRMED', 'RoomId': '',
    }
    h.update({k: str(v) for k, v in over.items()})
    r = urllib.request.Request(RIS + '/v1/ris_patient_search', headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}

st, d = search({})
rows = d.get('result') or []
print('status:', st, '| CONFIRMED orders:', len(rows))
for r in rows:
    print(f'{r.get("patient_name",""):24s} reg={r.get("registration_id")} study_no={r.get("study_number")} svc={r.get("service_name")} ord={r.get("order_date")}')
