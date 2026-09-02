import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
ctx = ssl.create_default_context()
BASE = 'https://nextgen.ehospital.gov.in/api/search/patient'

def post(path, payload):
    r = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
        headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json',
                 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(r, timeout=40, context=ctx) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}
    except Exception as e:
        return 'ERR', str(e)

for path in ['/patientSearch/1', '/patientLastVisitSearch/1', '/patientVisitSearch/1']:
    for payload in [
        {'SearchCri': 'Name', 'health_facility_id': '1246', 'pat_name': 'PATIENT_D'},
        {'SearchCri': 'Name', 'health_facility_id': '1246', 'patient_name': 'PATIENT_D'},
        {'SearchCri': 'NAME', 'health_facility_id': '1246', 'name': 'PATIENT_D'},
        {'name': 'PATIENT_D', 'health_facility_id': '1246'},
    ]:
        st, d = post(path, payload)
        names = []
        if isinstance(d, list):
            names = [(x.get('pat_f_name'), x.get('pat_uhid')) for x in d[:5]]
        elif isinstance(d, dict):
            names = [(d.get('pat_f_name'), d.get('pat_uhid'))]
        print(f'{path} | {payload["SearchCri"] if "SearchCri" in payload else payload} -> {st} {names}')
