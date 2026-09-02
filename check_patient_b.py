import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
ctx = ssl.create_default_context()

def call(method, url, headers=None, data=None):
    h = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Authorization': f'Bearer {token}'}
    if headers:
        h.update(headers)
    body = json.dumps(data).encode() if data is not None else None
    if data is not None:
        h['Content-Type'] = 'application/json'
    r = urllib.request.Request(url, data=body, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read()
        except Exception:
            return e.code, b''

# search PATIENT_B's orders
st, b = call('GET', 'https://nextgen.ehospital.gov.in/api/ris/api/ris/v1/ris_patient_search', {
    'healthFacilityId': HF, 'OrderDateStart': '', 'OrderDateEnd': '', 'ProcedureCategoryCode': '',
    'ProcedureId': '', 'RegistrationId': '202600XXXXX', 'StudyNumber': '', 'serviceStatus': '', 'RoomId': ''})
d = json.loads(b)
rows = d.get('result') or []
print('PATIENT_B orders:', len(rows))
for r in rows:
    print(f'  order_id={r.get("order_id")} svc_id={r.get("service_id")} status={r.get("service_status")} study_no={r.get("study_number")} svc={r.get("service_name")}')
    print(f'    report_title={r.get("report_title")!r} report_impression={r.get("report_impression")!r}')
    print(f'    report_description={(r.get("report_description") or "")[:60]!r}')

# get full report for the first row
if rows:
    r = rows[0]
    st, b = call('GET', 'https://nextgen.ehospital.gov.in/api/ris/api/ris/v1/report', {
        'serviceId': str(r['service_id']), 'orderId': str(r['order_id']),
        'healthFacilityId': HF, 'serviceStatus': str(r['service_status']), 'registrationId': str(r['registration_id'])})
    print('\ngetReport status:', st)
    print(b.decode('utf-8', 'replace')[:800])
