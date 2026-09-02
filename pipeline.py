"""
End-to-end: download MedTelerad 31/08 reports -> RIS Order Entry -> Report Creation -> Report Verification.
Usage:
  python pipeline.py --dry-run            # plan only, no writes
  python pipeline.py --limit N            # process first N patients
  python pipeline.py --patient UHID_A      # process one patient id (part before '/')
"""
import urllib.request, urllib.error, urllib.parse, http.cookiejar, ssl, os, re, json
import base64, io, subprocess, time, html as ihtml, sys, uuid
from collections import Counter
from PIL import Image
import ng_crypto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(BASE_DIR, 'config.json'), encoding='utf-8'))
MT = cfg['medtelerad']; NG = cfg['nextgen']
TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
ctx = ssl.create_default_context()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

# ============================== MedTelerad ==============================
def mt_login():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [('User-Agent', UA)]
    def hidden(h, name):
        m = re.search(r'<input[^>]*name="' + re.escape(name) + r'"[^>]*>', h)
        if not m:
            return ''
        v = re.search(r'value="([^"]*)"', m.group(0))
        return v.group(1) if v else ''
    h = op.open(MT['base'] + '/user/Login.aspx', timeout=30).read().decode('utf-8', 'replace')
    data = urllib.parse.urlencode({
        '__VIEWSTATE': hidden(h, '__VIEWSTATE'), '__VIEWSTATEGENERATOR': hidden(h, '__VIEWSTATEGENERATOR'),
        '__EVENTVALIDATION': hidden(h, '__EVENTVALIDATION'),
        'txtUser': MT['user'], 'txtPassword': MT['pass'], 'btnLogin': 'LOGIN',
    }).encode()
    req = urllib.request.Request(MT['base'] + '/user/Login.aspx', data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    op.open(req, timeout=30)
    return op, hidden

def mt_dashboard(op, hidden, page=None):
    if page is None:
        return op.open(MT['base'] + '/Patient/MedteleradDashboard.aspx', timeout=30).read().decode('utf-8', 'replace')
    dash = op.open(MT['base'] + '/Patient/MedteleradDashboard.aspx', timeout=30).read().decode('utf-8', 'replace')
    data = urllib.parse.urlencode({
        '__VIEWSTATE': hidden(dash, '__VIEWSTATE'), '__VIEWSTATEGENERATOR': hidden(dash, '__VIEWSTATEGENERATOR'),
        '__EVENTVALIDATION': hidden(dash, '__EVENTVALIDATION'),
        '__EVENTTARGET': 'gvTest', '__EVENTARGUMENT': f'Page${page}',
    }).encode()
    req = urllib.request.Request(MT['base'] + '/Patient/MedteleradDashboard.aspx', data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    return op.open(req, timeout=30).read().decode('utf-8', 'replace')

def mt_parse(dash):
    suids = re.findall(r'name="gvTest\$ctl\d+\$stUID"[^>]*value="([^"]+)"', dash)
    ptids = re.findall(r'name="gvTest\$ctl\d+\$ptID"[^>]*value="([^"]+)"', dash)
    ptnames = re.findall(r'name="gvTest\$ctl\d+\$ptName"[^>]*value="([^"]+)"', dash)
    rdates = re.findall(r'name="gvTest\$ctl\d+\$txtRDate"[^>]*value="([^"]+)"', dash)
    statuses = [m.group(1).strip() for m in re.finditer(r'__doPostBack\(&#39;gvTest\$ctl\d+\$lnkRpt&#39;,&#39;&#39;\)[^>]*>([^<]*)<', dash)]
    pages = [int(p) for p in re.findall(r'__doPostBack\(&#39;gvTest&#39;,&#39;Page\$(\d+)&#39;\)', dash)]
    studies = []
    for i in range(len(suids)):
        studies.append({'suid': suids[i], 'ptid': ptids[i] if i < len(ptids) else '',
                        'name': ptnames[i] if i < len(ptnames) else '',
                        'rdate': rdates[i] if i < len(rdates) else '',
                        'status': statuses[i] if i < len(statuses) else ''})
    return studies, pages

def mt_all_pages(op, hidden):
    dash = mt_dashboard(op, hidden)
    studies, pages = mt_parse(dash)
    max_page = max(pages) if pages else 1
    for p in range(2, max_page + 1):
        try:
            s2, _ = mt_parse(mt_dashboard(op, hidden, p))
            studies.extend(s2)
        except Exception as e:
            print(f'  [MT] page {p} error: {e!r}')
    seen = set(); uniq = []
    for s in studies:
        if s['suid'] not in seen:
            seen.add(s['suid']); uniq.append(s)
    return uniq

def parse_ptid(ptid):
    """Return (patient_id, study_no) handling normal, reversed, and 9-digit forms."""
    parts = ptid.split('/')
    p1 = parts[0].strip()
    p2 = parts[1].strip() if len(parts) > 1 else ''
    if len(p1) == 5:
        return p1, p2
    if len(p1) == 4 and len(p2) == 5:
        return p2, p1          # reversed: "study/patient"
    if len(p1) == 9 and p1.startswith('2026'):
        return p1[4:], p2      # "2026XXXXX" -> patient id = last 5
    if len(p1) == 11 and p1.startswith('2026'):
        return p1[6:], p2      # "202600XXXXX" -> patient id = last 5
    return None, None

def mt_report(op, suid):
    url = MT['base'] + '/report/FinalizedReport.aspx?UID=' + urllib.parse.quote(suid) + '&user=' + MT['user']
    rhtml = op.open(url, timeout=60).read().decode('utf-8', 'replace')
    def span(sid):
        m = re.search(r'id="' + sid + r'"[^>]*>([^<]*)<', rhtml)
        return m.group(1).strip() if m else ''
    m = re.search(r'<textarea id="txtTemplate1"[^>]*>(.*?)</textarea>', rhtml, re.S)
    raw = ihtml.unescape(m.group(1)) if m else ''
    clean = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
    clean = re.sub(r'<xml>.*?</xml>', '', clean, flags=re.S)
    proc_i = clean.find('PROCEDURE')
    if proc_i == -1:
        proc_i = clean.find('FINDINGS')
    start = clean.rfind('<p', 0, proc_i) if proc_i != -1 else 0
    if start == -1:
        start = proc_i if proc_i != -1 else 0
    date_i = clean.rfind('Date ')
    body = clean[start:date_i] if date_i > start else clean[start:]
    plain = re.sub(r'<[^>]+>', ' ', clean)
    plain = re.sub(r'\s+', ' ', plain)
    impression = ''
    imp_i = plain.upper().find('IMPRESSION')
    if imp_i != -1:
        seg = plain[imp_i:]
        mm = re.search(r'Date\s+\d', seg)
        if mm:
            seg = seg[:mm.start()]
        impression = re.sub(r'^IMPRESSION\s*:?\s*', '', seg, flags=re.I).strip()
    return {'patName': span('lblPatName'), 'patID': span('lblPatID'), 'study': span('lblStudy'),
            'modality': span('lblMod'), 'body_html': body, 'impression': impression}

# ============================== NextGen ==============================
def ng_req(method, url, headers=None, data=None, token=None):
    h = {'User-Agent': UA, 'Accept': 'application/json'}
    if headers:
        h.update(headers)
    if token:
        h['Authorization'] = 'Bearer ' + token
    body = None
    if data is not None:
        body = json.dumps(data).encode('utf-8')
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
    except Exception as e:
        return 'ERR', str(e).encode()

def ocr_captcha(img_bytes):
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    w, h = img.size
    votes = Counter()
    p = os.path.join(BASE_DIR, '.ctmp.png')
    for scale in (2, 3, 4):
        big = img.resize((w * scale, h * scale), Image.LANCZOS).convert('L')
        for thr in (None, 120, 150, 180):
            v = big if thr is None else big.point(lambda x: 255 if x > thr else 0)
            v.save(p)
            for psm in (7, 8):
                out = p + '.out'
                subprocess.run([TESS, p, out, '--psm', str(psm),
                                '-c', 'tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                try:
                    t = ''.join(ch for ch in open(out + '.txt').read().strip() if ch.isalnum())
                    if len(t) == 6:
                        votes[t] += 1
                except OSError:
                    pass
    return votes.most_common(1)[0][0] if votes else ''

def ng_login():
    # reuse a saved token if still valid
    saved = os.path.join(BASE_DIR, 'nextgen_session.json')
    if os.path.exists(saved):
        try:
            s0 = json.load(open(saved))
            if s0.get('access_token'):
                st, b = ng_req('GET', NG['base'] + '/api/user_mgmt/v1/users', {'healthFacilityId': str(s0.get('health_facility_id'))}, token=s0['access_token'])
                if st == 200:
                    print('[NG] reused saved token')
                    return s0, s0.get('__pubkey__', '')
        except Exception:
            pass
    st, b = ng_req('GET', NG['base'] + '/api/authentication/v1/pubkey')
    pubkey = json.loads(b)['result']['public_key']
    enc_pw = ng_crypto.rsa_encrypt_pkcs1_v15(pubkey, NG['pass'].encode('utf-8'))
    aes_key = pubkey[:16].encode('utf-8')
    for attempt in range(15):
        try:
            st, b = ng_req('GET', NG['base'] + '/api/authentication/v1/captcha_image', {'id': '', 'captchaId': ''})
            cap = json.loads(b)
            guess = ocr_captcha(base64.b64decode(cap['captchaImage']))
            st, b = ng_req('POST', NG['base'] + '/api/authentication/v1/login', data={
                'user_id': NG['user'], 'password': enc_pw, 'captcha_value': guess,
                'id': cap['id'], 'captcha_id': cap['captchaId']})
            resp = json.loads(b)
        except Exception as e:
            print(f'[NG] attempt {attempt} err: {e!r}')
            time.sleep(2)
            continue
        if resp.get('result'):
            plain = ng_crypto.aes128_ecb_decrypt(aes_key, base64.b64decode(resp['result']))
            d = json.loads(plain)
            d['user_id'] = NG['user']
            d['__pubkey__'] = pubkey
            json.dump(d, open(os.path.join(BASE_DIR, 'nextgen_session.json'), 'w'), indent=2)
            print(f'[NG] login OK (captcha {guess!r})')
            return d, pubkey
        if 'captcha' not in resp.get('metadata', {}).get('message', '').lower():
            print('[NG] login failed:', resp.get('metadata', {}).get('message'))
            break
        time.sleep(1)
    raise SystemExit('could not login to NextGen')

def patient_search(token, hf, uhid):
    st, b = ng_req('POST', NG['base'] + '/api/search/patient/patientLastVisitSearch/1',
                   data={'SearchCri': 'UHID', 'health_facility_id': str(hf), 'pat_uhid': uhid}, token=token)
    try:
        rows = json.loads(b)
        return st, (rows[0] if rows else None)
    except Exception:
        return st, None

def load_services():
    return json.load(open(os.path.join(BASE_DIR, 'ris_services.json')))

def match_service(study, modality, services):
    s = (study or '').upper()
    m = (modality or '').upper()
    best, best_score = None, -1
    for cat_code, cat in services.items():
        for it in cat['items']:
            name = (it.get('service_item_name') or '').upper()
            score = 0
            for kw in re.findall(r'[A-Z0-9]{2,}', s):
                if kw in name:
                    score += 2
                elif kw in cat['category_name'].upper():
                    score += 1
            if 'X-RAY' in m or 'XRAY' in m:
                if 'X-RAY' in name or 'XRAY' in name or 'X RAY' in name:
                    score += 1
            if 'USG' in m or 'ULTRASOUND' in m:
                if 'USG' in name or 'ULTRASOUND' in name:
                    score += 1
            if score > best_score:
                best_score = score
                best = (cat_code, cat['category_name'], it)
    return best

def order_entry(token, hf, user_id, patient, cat_code, cat_name, item):
    uhid = patient['pat_uhid']
    f = patient.get('pat_f_name') or ''
    m = patient.get('pat_m_name') or ''
    l = patient.get('pat_l_name') or ''
    addr = patient.get('address') or {}
    dob = (patient.get('pat_dob') or '').strip()
    # dd/MM/yyyy -> yyyy-MM-dd and yyyy/MM/dd
    dob_a, dob_b = dob, dob
    mm = re.match(r'(\d{2})/(\d{2})/(\d{4})', dob)
    if mm:
        d, mo, y = mm.group(1), mm.group(2), mm.group(3)
        dob_a = f'{y}-{mo}-{d}'
        dob_b = f'{y}/{mo}/{d}'
    item_obj = {
        'service_item_code': item.get('service_item_code'), 'service_item_name': item.get('service_item_name'),
        'service_type_code': item.get('service_type_code'), 'service_type_name': item.get('service_type_name'),
        'specimen_id': item.get('specimen_id'), 'specimen_name': item.get('specimen_name'),
        'service_provider_id': item.get('service_provider_id'), 'service_provider_name': item.get('service_provider_name'),
    }
    # Step A: patient_registration
    reg_payload = {
        'health_facility_id': hf, 'patient_registration_id': uhid,
        'patient_f_name': f, 'patient_m_name': m, 'patient_l_name': l,
        'gender_code': patient.get('gender_code'), 'pat_mobile': patient.get('pat_mobile'),
        'address_line': addr.get('address_line'), 'dist_code': addr.get('dist_code'),
        'pat_dob': dob_a, 'state_code': addr.get('state_code'),
        'order_resistration_object': [{
            'service_category_code': cat_code, 'service_category_name': cat_name,
            'ObservationEntryServiceItem': [item_obj], 'optionFilter': '',
        }],
        'registration_type': patient.get('patient_registration_type'),
        'visit_id': patient.get('pat_visit_id'), 'patient_appellation': patient.get('appellation_value'),
        'visit_no': patient.get('visit_no'), 'encounter_date': patient.get('visit_date'),
        'abha_address': patient.get('pat_health_id'), 'abha_number': patient.get('pat_health_id_number'),
        'department_code': patient.get('department_code'), 'department_name': patient.get('department_value'),
    }
    st_a, b_a = ng_req('POST', NG['base'] + '/api/ris/api/ris/v1/patient_registration', data=reg_payload, token=token)

    # Step B: centralized order entry
    order_id = str(uuid.uuid4())
    entry = {
        'health_facility_abdm_hfid': patient.get('hf_id_abdm') or '',
        'health_facility_id': hf, 'ipd_id': '', 'order_by_user_id': user_id,
        'order_entry_details': [{
            'advice': '', 'method_id': None, 'method_name': None, 'orderEntryStatus': 'ORDERED', 'quantity': 1,
            'service_category_code': cat_code, 'service_category_name': cat_name,
            'service_item_code': item_obj['service_item_code'], 'service_item_name': item_obj['service_item_name'],
            'service_type_code': item_obj['service_type_code'], 'service_type_name': item_obj['service_type_name'],
            'service_wise_order_id': str(uuid.uuid4()), 'specimen_id': item_obj['specimen_id'],
            'specimen_name': item_obj['specimen_name'], 'service_provider_id': item_obj['service_provider_id'],
            'service_provider_name': item_obj['service_provider_name'], 'service_provider_short_name': '',
        }],
        'order_entry_source_module_description': 'RIS', 'order_entry_source_module_id': '12',
        'order_id': order_id, 'patient_class_code': patient.get('patient_class_code') or '',
        'registration_type': patient.get('patient_registration_type'), 'service_item_order_entry_active_status': 1,
        'service_order_entry_done_on_behalf_of_user_id': '',
        'visit_id': patient.get('pat_visit_id'), 'visit_no': patient.get('visit_no') or '1',
        'visit_date': patient.get('visit_date') or '', 'patient_uhid': uhid,
        'patient_f_name': f, 'patient_m_name': m, 'patient_l_name': l, 'patient_dob': dob_b,
        'patient_mobile_no': patient.get('pat_mobile'), 'patient_address': addr.get('address_line'),
        'patient_appelation_value': patient.get('appellation_value'), 'patient_gender': patient.get('gender_code'),
        'patient_ward_no': '', 'patient_admission_date': '',
        'patient_abha_id': patient.get('pat_health_id'), 'patient_abha_no': patient.get('pat_health_id_number'),
        'patient_guardian_name': '', 'patient_beneficiary_id': '',
        'patient_scheme_id': '', 'patient_scheme_name': '',
        'department_name': patient.get('department_value'), 'doctor_name': patient.get('practitioner_name') or '',
    }
    st_b, b_b = ng_req('POST', NG['base'] + '/api/centralized_patient/v1/centralized_patient_service_order_entry',
                       data=entry, token=token)
    return st_a, b_a, st_b, b_b, order_id

def ris_search(token, hf, reg_id):
    st, b = ng_req('GET', NG['base'] + '/api/ris/api/ris/v1/ris_patient_search', {
        'healthFacilityId': str(hf), 'OrderDateStart': '', 'OrderDateEnd': '', 'ProcedureCategoryCode': '',
        'ProcedureId': '', 'RegistrationId': reg_id, 'StudyNumber': '', 'serviceStatus': '', 'RoomId': '',
    }, token=token)
    try:
        return st, (json.loads(b).get('result') or [])
    except Exception:
        return st, []

FINDING_AI = {
    'Infiltration/Consolidation': '', 'Emphysema': '', 'Edema': '', 'Atelectasis': '',
    'Nodule/Mass': '', 'Pneumothorax': '', 'Fibrosis': '', 'Cardiomegaly': '',
    'Hernia': '', 'Effusion': '', 'Pleural Thickening': '', 'remarks': '',
}

def create_report(token, hf, user_id, user_name, row, body_html, impression):
    payload = {
        'health_facility_id': hf, 'remarks': '', 'order_id': row.get('order_id'),
        'registration_id': row.get('registration_id'), 'report_description': body_html,
        'report_impression': impression, 'report_prepared_by': user_name, 'report_title': '',
        'service_id': row.get('service_id'), 'is_draft_report': 0,
        'report_prepared_by_id': user_id, 'finding_ai': FINDING_AI,
    }
    return ng_req('POST', NG['base'] + '/api/ris/api/ris/v1/report', data=payload, token=token)

def verify_report(token, hf, user_id, user_name, row, body_html, impression):
    payload = {
        'report_impression': impression, 'report_description': body_html, 'health_facility_id': hf,
        'order_id': row.get('order_id'), 'registration_id': row.get('registration_id'),
        'report_title': None, 'service_id': row.get('service_id'),
        'report_verified_by': user_name, 'report_verified_by_id': user_id,
    }
    return ng_req('POST', NG['base'] + '/api/ris/api/ris/v1/report_verification', data=payload, token=token)

# ============================== Main ==============================
def main():
    dry_run = '--dry-run' in sys.argv
    limit = None; patient = None
    for i, a in enumerate(sys.argv):
        if a == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
        if a == '--patient' and i + 1 < len(sys.argv):
            patient = sys.argv[i + 1]

    op, hidden = mt_login()
    print('[MT] logged in')
    studies = mt_all_pages(op, hidden)
    print(f'[MT] total studies: {len(studies)}')
    targets = [s for s in studies if '2026-08-30' in s['rdate'] and s['status'] == 'Final']
    print(f'[MT] 30/08 Final reports: {len(targets)}')

    sess, pubkey = ng_login()
    token = sess['access_token']; hf = sess['health_facility_id']
    user_id = sess.get('user_id') or NG['user']
    user_name = ' '.join(((sess.get('f_name') or '') + ' ' + (sess.get('m_name') or '') + ' ' + (sess.get('l_name') or '')).split())
    services = load_services()
    print(f'[NG] user={user_id!r} hf={hf}')

    results = []
    for idx, s in enumerate(targets):
        if patient and s['ptid'].split('/')[0] != patient:
            continue
        if limit is not None and len(results) >= limit:
            break
        pid, study_no = parse_ptid(s['ptid'])
        uhid = ('202600' + pid) if pid and len(pid) == 5 else None
        if not uhid:
            print(f'[skip] {s["name"]}: bad ptid {s["ptid"]!r}')
            results.append({'name': s['name'], 'ptid': s['ptid'], 'note': 'bad ptid'})
            continue
        rep = mt_report(op, s['suid'])
        matched = match_service(rep['study'], rep['modality'], services)
        if not matched:
            print(f'[skip] {s["name"]} ({s["ptid"]}): no service match for {rep["study"]!r}')
            results.append({'name': s['name'], 'ptid': s['ptid'], 'note': f'no service for {rep["study"]}'})
            continue
        cat_code, cat_name, item = matched
        st, pat = patient_search(token, hf, uhid)
        if st != 200 or not pat:
            print(f'[skip] {s["name"]} ({s["ptid"]}): patient {uhid} not found (st={st})')
            results.append({'name': s['name'], 'ptid': s['ptid'], 'note': f'patient {uhid} not found'})
            continue
        reg_name = ' '.join(((pat.get('pat_f_name') or '') + ' ' + (pat.get('pat_m_name') or '') + ' ' + (pat.get('pat_l_name') or '')).split()).lower()
        mt_name = ' '.join(s['name'].split()).lower()
        if reg_name and mt_name and reg_name != mt_name:
            print(f'[skip] {s["name"]} ({s["ptid"]}): name mismatch (registry {reg_name!r})')
            results.append({'name': s['name'], 'ptid': s['ptid'], 'note': f'name mismatch: {reg_name}'})
            continue
        # pre-check: skip only if this patient already has a REPORT_VERIFIED order for the SAME service
        st_pre, rows_pre = ris_search(token, hf, uhid)
        svc_code = str(item['service_item_code'])
        if any(r.get('service_status') == 'REPORT_VERIFIED' and str(r.get('service_id')) == svc_code for r in rows_pre):
            print(f'[skip] {s["name"]} ({s["ptid"]}): already REPORT_VERIFIED for {item["service_item_name"]}')
            results.append({'name': s['name'], 'ptid': s['ptid'], 'note': 'already verified (same service)'})
            continue
        print(f'[{idx}] {s["name"]} | UHID={uhid} | study={rep["study"]} | svc={item["service_item_name"]} ({item["service_item_code"]})')
        if dry_run:
            results.append({'name': s['name'], 'uhid': uhid, 'study': rep['study'], 'svc': item['service_item_name'], 'action': 'order+report+verify'})
            continue
        st_a, b_a, st_b, b_b, order_id = order_entry(token, hf, user_id, pat, cat_code, cat_name, item)
        print(f'     orderA(patient_registration) -> {st_a}: {b_a[:200].decode("utf-8","replace")}')
        print(f'     orderB(centralized entry)     -> {st_b}: {b_b[:200].decode("utf-8","replace")}')
        if st_a != 200 or st_b != 200:
            results.append({'name': s['name'], 'uhid': uhid, 'note': f'order entry failed A={st_a} B={st_b}', 'respA': b_a[:200].decode('utf-8','replace'), 'respB': b_b[:200].decode('utf-8','replace')})
            continue
        # find the new order (CONFIRMED) to get order_id/service_id
        time.sleep(2)
        st, rows = ris_search(token, hf, uhid)
        pending = [r for r in rows if r.get('service_status') != 'REPORT_VERIFIED']
        row = (pending or rows)[0] if rows else None
        if not row:
            results.append({'name': s['name'], 'uhid': uhid, 'note': 'order not found after entry'})
            continue
        cst, cb = create_report(token, hf, user_id, user_name, row, rep['body_html'], rep['impression'])
        print(f'     report create -> {cst}: {cb[:200].decode("utf-8","replace")}')
        vst, vb = verify_report(token, hf, user_id, user_name, row, rep['body_html'], rep['impression'])
        print(f'     report verify -> {vst}: {vb[:200].decode("utf-8","replace")}')
        results.append({'name': s['name'], 'uhid': uhid, 'orderA': st_a, 'orderB': st_b, 'create': cst, 'verify': vst})

    print('\n===== SUMMARY =====')
    for r in results:
        print(r)
    json.dump(results, open(os.path.join(BASE_DIR, 'pipeline_results.json'), 'w'), indent=2, ensure_ascii=False)
    print('saved pipeline_results.json')

if __name__ == '__main__':
    main()
