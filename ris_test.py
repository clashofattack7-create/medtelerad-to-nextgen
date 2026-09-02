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
        with urllib.request.urlopen(r, timeout=40, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 'ERR', str(e).encode()

for auth in [f'Bearer {token}', token]:
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'Authorization': auth,
        'healthFacilityId': HF,
        'OrderDateStart': '', 'OrderDateEnd': '',
        'ProcedureCategoryCode': '', 'ProcedureId': '',
        'RegistrationId': '202600XXXXX',
        'StudyNumber': '5161',
        'serviceStatus': '', 'RoomId': '',
    }
    st, b = get(RIS + '/v1/ris_patient_search', headers)
    print(f'=== auth prefix: {auth[:15]}... ===')
    print('status:', st)
    print(b[:1500].decode('utf-8', 'replace'))
    print()
