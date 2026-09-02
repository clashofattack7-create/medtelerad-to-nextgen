# Full reverse-engineering notes (complete)

## Credentials (config.json)
- MedTelerad: STAFF_USER_A / (in config) — tele.medtelerad.com
- NextGen RIS: STAFF_USER_B / (in config) — nextgen.ehospital.gov.in

## Patient ID mapping (from user)
- MedTelerad ptID "UHID_A/STUDY_A" => RIS UHID = "202600" + "UHID_A" = "202600XXXXX"; study number = "STUDY_A".

## MedTelerad (source) — WORKING
- Login: POST /user/Login.aspx (txtUser, txtPassword, btnLogin=LOGIN + VIEWSTATE/EVENTVALIDATION).
- Dashboard: /Patient/MedteleradDashboard.aspx — grid gvTest, rdate = "2026-08-31 ...".
- Report: /report/FinalizedReport.aspx?UID=<stUID>&user=STAFF_USER_A
  - textarea txtTemplate1 = Word-HTML report (strip XML comments/<xml> blocks).
  - Sections: patient table, PROCEDURE, FINDINGS, IMPRESSION, "Date ... Time ...".
  - lblPatName, lblPatID, lblStudy (study type), lblMod (modality).
- PDF: POST btnPdf=Download in PDF -> application/pdf.

## NextGen login — WORKING (ng_crypto.py)
- GET /api/authentication/v1/pubkey -> {result:{public_key: base64 SPKI RSA-4096}}
- GET /api/authentication/v1/captcha_image (headers id, captchaId) -> {captchaImage(base64 jpeg), id, captchaId}
- POST /api/authentication/v1/login {user_id, password(RSA PKCS#1 v1.5 b64), captcha_value, id, captcha_id}
- Login result = AES-128-ECB (PKCS7), key = pubkey_b64[:16].utf8.
- Token: Bearer <access_token>. user_id = "STAFF_USER_B". health_facility_id = 1246.

## RIS patient search
- POST /api/search/patient/patientLastVisitSearch/1 {SearchCri:"UHID", health_facility_id, pat_uhid}
  -> returns patient[0] demographics (pat_uhid, pat_f_name, gender_code, pat_dob, pat_mobile, address{address_line,state_code,dist_code}, patient_class_code, patient_registration_type, pat_visit_id, visit_no, visit_date, department_code/value, appellation_value, ...).
- GET /api/ris/api/ris/v1/ris_patient_search (headers healthFacilityId, RegistrationId, StudyNumber, serviceStatus, OrderDateStart/End, ...).

## RIS services (billingConfig base = /api/billing/billconf)
- GET /v1/service_category/ (healthFacilityId) -> service_category_details; radiology = service_type_code 16.
- Radiology categories: 130 CT Scan, 132 NCCT, 111 Routine Ultrasound, 109 Routine X-Ray.
- GET /v1/servicesByServiceCategoryCode/ (healthFacilityId, serviceCategoryCode) -> items.
- Key items: 1301000538 C T Scan Thorax/HRCT plain; 2000000046 CT Brain (Head) Plain; 1111000116 ABDOMEN USG; 1091001080 CHEST PA DIGITAL; 1091002567 PNS AP/LAT XRAY; 2000000061 CT Urography.
- Saved to ris_services.json.

## Order entry (Radiology Transaction)
Step A: POST /api/ris/api/ris/v1/patient_registration  (addRegistrationform.value)
  fields: health_facility_id, patient_registration_id(=pat_uhid), patient_f_name, patient_m_name, patient_l_name,
  gender_code, pat_mobile, address_line, dist_code, pat_dob, state_code,
  order_resistration_object:[{service_category_code, service_category_name, ObservationEntryServiceItem:[item], optionFilter:""}],
  registration_type, visit_id, patient_appellation, visit_no, encounter_date, abha_address, abha_number, department_code, department_name.
  item = {service_item_code, service_item_name, service_type_code, service_type_name, specimen_id, specimen_name, service_provider_id, service_provider_name}.
Step B: POST /api/centralized_patient/v1/centralized_patient_service_order_entry
  { health_facility_abdm_hfid, health_facility_id, ipd_id:"", order_by_user_id,
    order_entry_details:[{advice:"",method_id:null,method_name:null,orderEntryStatus:"ORDERED",quantity:1,
      service_category_code, service_category_name, service_item_code, service_item_name,
      service_type_code, service_type_name, service_wise_order_id(uuid), specimen_id, specimen_name,
      service_provider_id, service_provider_name, service_provider_short_name:""}],
    order_entry_source_module_description:"RIS", order_entry_source_module_id:"12", order_id(uuid v5),
    patient_class_code, registration_type, service_item_order_entry_active_status:1,
    service_order_entry_done_on_behalf_of_user_id:"", visit_id, visit_no, visit_date,
    patient_uhid, patient_f_name, patient_m_name, patient_l_name, patient_dob, patient_mobile_no,
    patient_address, patient_appelation_value, patient_gender, patient_ward_no:"", patient_admission_date:"",
    patient_abha_id, patient_abha_no, patient_guardian_name:"", patient_beneficiary_id:"",
    patient_scheme_id:"", patient_scheme_name:"", department_name, doctor_name }

## Report creation / verification — WORKING payloads
- POST /api/ris/api/ris/v1/report  (ReportCreation)
  { health_facility_id, remarks:"", order_id, registration_id, report_description(HTML), report_impression,
    report_prepared_by:"Radiology DOD", report_title:null, service_id, is_draft_report:0,
    report_prepared_by_id:"STAFF_USER_B", finding_ai:null }
- POST /api/ris/api/ris/v1/report_verification
  { report_impression, report_description, health_facility_id, order_id, registration_id,
    report_title:null, service_id, report_verified_by:"Radiology DOD", report_verified_by_id:"STAFF_USER_B" }
