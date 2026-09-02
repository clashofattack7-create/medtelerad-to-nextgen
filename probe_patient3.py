import sys, json, io
sys.path.insert(0, r'D:\dsh\DSH\medtelerad-to-nextgen')
from pipeline import mt_login, mt_all_pages, mt_report, parse_ptid, ng_login, ris_search
import urllib.request, urllib.error, ssl, os

op, hidden = mt_login()
studies = mt_all_pages(op, hidden)
target = [s for s in studies if parse_ptid(s['ptid'])[0] == 'UHID_C' and s['status'] == 'Final'][0]
rep = mt_report(op, target['suid'])

sess, pubkey = ng_login()
token = sess['access_token']; hf = sess['health_facility_id']
st2, rows = ris_search(token, hf, '202600XXXXX')
r = rows[0]

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
d = json.loads(b)
x = (d.get('result') or [])[0]
ris_desc = x.get('report_description') or ''
ris_imp = x.get('report_impression') or ''

mt_body = rep['body_html']
mt_imp = rep['impression']
print('medtelerad body len  :', len(mt_body))
print('ris report desc len  :', len(ris_desc))
print('body identical       :', mt_body == ris_desc)
if mt_body != ris_desc:
    i = next((k for k in range(min(len(mt_body), len(ris_desc))) if mt_body[k] != ris_desc[k]), None)
    print('first diff at:', i)
    print('MT :', repr(mt_body[i-80:i+80]))
    print('RIS:', repr(ris_desc[i-80:i+80]))
print('medtelerad impression:', repr(mt_imp))
print('ris impression       :', repr(ris_imp))
print('impression identical :', mt_imp == ris_imp)
print()
print('order_id      :', r.get('order_id'))
print('service_id    :', r.get('service_id'))
print('service_name  :', r.get('service_name'))
print('status        :', r.get('service_status'))
print('created       :', r.get('report_creation_date'))
print('verified      :', r.get('report_verification_date'))
print('DONE')
