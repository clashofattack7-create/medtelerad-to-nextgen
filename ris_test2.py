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
    except Exception as e:
        return 'ERR', str(e).encode()

def search(**over):
    h = {
        'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'healthFacilityId': HF,
        'OrderDateStart': '', 'OrderDateEnd': '',
        'ProcedureCategoryCode': '', 'ProcedureId': '',
        'RegistrationId': '', 'StudyNumber': '',
        'serviceStatus': '', 'RoomId': '',
    }
    h.update({k: str(v) for k, v in over.items()})
    st, b = get(RIS + '/v1/ris_patient_search', h)
    return st, b

# 1. broad search with yesterday-today date range
print('=== broad search (dates 31/08/2026..01/09/2026) ===')
st, b = search(OrderDateStart='31/08/2026', OrderDateEnd='01/09/2026')
print('status:', st, '| bytes:', len(b))
print(b[:2500].decode('utf-8', 'replace'))
