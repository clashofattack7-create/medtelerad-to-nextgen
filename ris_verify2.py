import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
RIS = 'https://nextgen.ehospital.gov.in/api/ris/api/ris'
ctx = ssl.create_default_context()

def search(reg, study):
    h = {
        'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'healthFacilityId': HF,
        'OrderDateStart': '', 'OrderDateEnd': '',
        'ProcedureCategoryCode': '', 'ProcedureId': '',
        'RegistrationId': reg, 'StudyNumber': study,
        'serviceStatus': '', 'RoomId': '',
    }
    r = urllib.request.Request(RIS + '/v1/ris_patient_search', headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}

tests = [
    ('202600XXXXX', 'STUDY_A', 'PATIENT_B'),
    ('202600XXXXX', 'STUDY_C', 'PATIENT_C'),
    ('202600UHID_C', 'STUDY_B', 'PATIENT_E'),
    ('202600UHID_B', 'STUDY_C', 'PATIENT_F '),
]
for reg, study, name in tests:
    st, d = search(reg, study)
    rows = d.get('result') or []
    names = [r.get('patient_name') for r in rows]
    statuses = [r.get('service_status') for r in rows]
    services = [r.get('service_name') for r in rows]
    print(f'{name}: reg={reg} study={study} -> {st}')
    for n, s, sv in zip(names, statuses, services):
        print(f'     {n} | {s} | {sv}')
