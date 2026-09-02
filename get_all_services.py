import urllib.request, urllib.error, json, ssl, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sess = json.load(open(os.path.join(BASE_DIR, 'nextgen_session.json')))
token = sess['access_token']
HF = str(sess['health_facility_id'])
ctx = ssl.create_default_context()
BILL = 'https://nextgen.ehospital.gov.in/api/billing/billconf'

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

cats = {'130': 'CT Scan', '132': 'NCCT', '111': 'Routine Ultrasound', '109': 'Routine X-Ray'}
out = {}
for code, name in cats.items():
    st, d = get(BILL + '/v1/servicesByServiceCategoryCode/', {'healthFacilityId': HF, 'serviceCategoryCode': code})
    items = d.get('result') or []
    out[code] = {'category_name': name, 'items': [{k: it.get(k) for k in ['service_item_code', 'service_item_name', 'service_type_code', 'service_type_name', 'specimen_id', 'specimen_name', 'service_provider_id', 'service_provider_name']} for it in items]}
    print(f'=== {code} {name}: {len(items)} items ===')
    for it in items:
        print(f'   {it.get("service_item_code")} = {it.get("service_item_name")}')

json.dump(out, open(os.path.join(BASE_DIR, 'ris_services.json'), 'w'), indent=2, ensure_ascii=False)
print('\nsaved ris_services.json')
