import sys, json, io
sys.path.insert(0, r'D:\dsh\DSH\medtelerad-to-nextgen')
import pipeline as P
from pipeline import mt_login, mt_all_pages, mt_report, parse_ptid, ng_login, patient_search, ris_search
import urllib.request, urllib.error, ssl, os

op, hidden = mt_login()
studies = mt_all_pages(op, hidden)
target = [s for s in studies if parse_ptid(s['ptid'])[0] == 'UHID_C' and s['status'] == 'Final'][0]
rep = mt_report(op, target['suid'])
print('=== MEDTELERAD REPORT ===')
print('body_html (' + str(len(rep['body_html'])) + ' chars):')
print(rep['body_html'][:2500])
print()
print('impression:', repr(rep['impression']))

sess, pubkey = ng_login()
token = sess['access_token']; hf = sess['health_facility_id']
st2, rows = ris_search(token, hf, '202600XXXXX')
r = rows[0]
print()
print('=== EXISTING RIS ORDER ===')
for k in ['registration_id','order_id','service_id','service_status','service_name','report_creation_date','report_verification_date','study_number']:
    print(f'  {k}: {r.get(k)}')

def get(url, headers):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Authorization': 'Bearer ' + token}
    h.update(headers)
    req = urllib.request.Request(url, headers=h)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

st, b = get('https://nextgen.ehospital.gov.in/api/ris/api/ris/v1/report', {
    'serviceId': str(r['service_id']), 'orderId': str(r['order_id']), 'healthFacilityId': str(hf),
    'serviceStatus': str(r['service_status']), 'registrationId': str(r['registration_id'])})
print()
print('GET /v1/report -> st', st, 'bytes', len(b))
try:
    d = json.loads(b)
    res = d.get('result') or []
    if res:
        x = res[0]
        print('report_impression:', repr(x.get('report_impression')))
        print()
        print('report_description (' + str(len(x.get('report_description') or '')) + ' chars):')
        print((x.get('report_description') or '')[:2500])
    else:
        print('no result in payload:', b[:500])
except Exception as e:
    print('parse err', e, b[:500])
