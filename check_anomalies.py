import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
ctx = ssl.create_default_context()

def search(uhid):
    r = urllib.request.Request('https://nextgen.ehospital.gov.in/api/search/patient/patientLastVisitSearch/1',
        data=json.dumps({'SearchCri': 'UHID', 'health_facility_id': '1246', 'pat_uhid': uhid}).encode(),
        headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(r, timeout=40, context=ctx) as resp:
            rows = json.loads(resp.read())
            return rows[0]['pat_f_name'] if rows else None
    except urllib.error.HTTPError as e:
        return f'HTTP {e.code}'
    except Exception as e:
        return f'ERR {e}'

print('SHUBRA MONI (ptid 202600XXXXX/5161) candidates:')
for u in ['202600XXXXX', '202600XXXXX', '202600XXXXX', '202600XXXXX']:
    print(f'  {u} -> {search(u)}')

print('HARKUMAR BISWAS (ptid 5159/66113) candidates:')
for u in ['202600XXXXX', '202600XXXXX', '202600XXXXX', '202600XXXXX']:
    print(f'  {u} -> {search(u)}')
