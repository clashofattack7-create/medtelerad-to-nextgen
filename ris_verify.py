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

def search_reg(reg):
    h = {
        'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'healthFacilityId': HF,
        'OrderDateStart': '', 'OrderDateEnd': '',
        'ProcedureCategoryCode': '', 'ProcedureId': '',
        'RegistrationId': reg, 'StudyNumber': '',
        'serviceStatus': '', 'RoomId': '',
    }
    st, b = get(RIS + '/v1/ris_patient_search', h)
    try:
        d = json.loads(b)
        rows = d.get('result') or []
        names = [r.get('patient_name') for r in rows]
        return st, names[:5]
    except Exception:
        return st, [b[:200].decode('utf-8', 'replace')]

# MedTelerad patient ID -> predicted RIS registration_id = "2026"+"00"+id
tests = {
    'UHID_A': '202600XXXXX',   # PATIENT_B
    'UHID_B': '202600UHID_B',   # PATIENT_F  (known match)
    'UHID_C': '202600XXXXX',   # PATIENT_C
    'UHID_C': '202600UHID_C',   # PATIENT_E
    'UHID_D': '202600UHID_D',   # PATIENT_G
    'UHID_E': '202600UHID_E',   # PATIENT_H
    'UHID_F': '202600UHID_F',   # PATIENT_I
}
for pid, reg in tests.items():
    st, names = search_reg(reg)
    print(f'MedTelerad {pid} -> RIS {reg}: status={st} names={names}')
