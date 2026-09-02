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

# service categories
st, d = get(BILL + '/v1/service_category/', {'healthFacilityId': HF})
print('service_category status:', st)
cats = []
if isinstance(d, dict) and d.get('result'):
    cats = d['result'][0].get('service_category_details', []) if isinstance(d['result'], list) else d['result']
elif isinstance(d, list):
    cats = d
print('total categories:', len(cats))
rad = [c for c in cats if str(c.get('service_type_code')) == '16']
print('radiology categories (type 16):', len(rad))
for c in rad:
    print(f'  cat_code={c.get("service_category_code")} name={c.get("service_category_short_name") or c.get("service_category_name")}')

# service items for first radiology category
if rad:
    cc = rad[0]['service_category_code']
    st, d = get(BILL + '/v1/servicesByServiceCategoryCode/', {'healthFacilityId': HF, 'serviceCategoryCode': str(cc)})
    print(f'\nservices for category {cc}: status {st}')
    items = d.get('result') or []
    for it in items[:60]:
        print(f'  item_code={it.get("service_item_code")} name={it.get("service_item_name")}')
