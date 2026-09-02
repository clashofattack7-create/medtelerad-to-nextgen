import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
ctx = ssl.create_default_context()

def get(url, headers):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    h.update(headers)
    r = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}

st, d = get('https://nextgen.ehospital.gov.in/api/ris/api/ris/v1/ris_patient_search', {
    'healthFacilityId': HF, 'OrderDateStart': '', 'OrderDateEnd': '', 'ProcedureCategoryCode': '',
    'ProcedureId': '', 'RegistrationId': '202600XXXXX', 'StudyNumber': '', 'serviceStatus': '', 'RoomId': ''})
rows = d.get('result') or []
print('PATIENT_A (202600XXXXX) orders:', len(rows))
for r in rows:
    print(f'  order_id={r.get("order_id")} svc_id={r.get("service_id")} status={r.get("service_status")} study_no={r.get("study_number")} svc={r.get("service_name")}')
    print(f'    registration={r.get("registration_id")} patient={r.get("patient_name")}')
