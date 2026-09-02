import sys, json, io
sys.path.insert(0, r'D:\dsh\DSH\medtelerad-to-nextgen')
import pipeline as P
from pipeline import mt_login, mt_all_pages, mt_report, parse_ptid, ng_login, patient_search, ris_search, match_service, load_services

op, hidden = mt_login()
print('[MT] logged in')
studies = mt_all_pages(op, hidden)
print(f'[MT] total studies: {len(studies)}')
cands = []
for s in studies:
    pid, sno = parse_ptid(s['ptid'])
    if pid and pid == 'UHID_C':
        cands.append(s)
print(f'[MT] studies for ptid UHID_C: {len(cands)}')
for s in cands:
    print(f'  suid={s["suid"]} ptid={s["ptid"]} name={s["name"]!r} rdate={s["rdate"]!r} status={s["status"]!r}')

target = None
for s in cands:
    pid, sno = parse_ptid(s['ptid'])
    if str(sno) == 'STUDY_C' and s['status'] == 'Final':
        target = s; break
if target is None:
    for s in cands:
        if s['status'] == 'Final':
            target = s; break
if target is None:
    print('NO FINAL STUDY FOUND'); sys.exit(0)

rep = mt_report(op, target['suid'])
print(f'REPORT for suid {target["suid"]}: name={rep["patName"]!r} patID={rep["patID"]!r} study={rep["study"]!r} modality={rep["modality"]!r}')
print(f'  body_html len={len(rep["body_html"])}')
print(f'  impression={rep["impression"][:200]!r}')

sess, pubkey = ng_login()
token = sess['access_token']; hf = sess['health_facility_id']
print(f'[NG] hf={hf} token len={len(token)}')
uhid = '202600XXXXX'
st, pat = patient_search(token, hf, uhid)
print(f'[NG] patient_search st={st}')
if pat:
    nm = ' '.join(((pat.get('pat_f_name') or '') + ' ' + (pat.get('pat_m_name') or '') + ' ' + (pat.get('pat_l_name') or '')).split())
    print(f'  pat name={nm!r} gender={pat.get("gender_code")} dob={pat.get("pat_dob")} visit={pat.get("pat_visit_id")}/{pat.get("visit_no")} dept={pat.get("department_value")}')
else:
    print('  PATIENT NOT FOUND IN RIS')
st2, rows = ris_search(token, hf, uhid)
print(f'[NG] ris_search st={st2} rows={len(rows)}')
for r in rows:
    print(f'  order_id={r.get("order_id")} svc_id={r.get("service_id")} status={r.get("service_status")} svc={r.get("service_name")} reg={r.get("registration_id")}')
    print(f'    study_no={r.get("study_number")} order_date={r.get("order_date")} patient={r.get("patient_name")}')
services = load_services()
matched = match_service(rep['study'], rep['modality'], services)
if matched:
    print(f'[SVC] matched: cat={matched[1]} / item={matched[2].get("service_item_name")} ({matched[2].get("service_item_code")})')
else:
    print('[SVC] NO MATCH')
print('PROBE DONE')
