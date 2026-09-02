# medtelerad-to-nextgen

Scripts used to migrate radiology reports from the **MedTelerad** platform to a
**NextGen RIS** environment.

## What's here

- Authentication flows for both platforms (form login, RSA public-key password
  encryption, session/token handling)
- CAPTCHA image retrieval and OCR solving pipeline
- Patient and study search by UHID / name / visit
- Order entry payload construction
- Report retrieval, parsing, and verification probes
- Reverse-engineering notes in `NOTES.md` (API endpoints, payload layouts)

## Notes on data

All patient identifiers and account names in the scripts and notes have been
redacted to generic placeholders (`PATIENT_A`..., `UHID_X`, `STAFF_USER_A`).
Live credentials are never committed — they live in `config.json` (git-ignored).

## Requirements

- Python 3+
- `requests`, `cryptography` (install as needed)
- Tesseract OCR for the CAPTCHA pipeline

## License

MIT — see [LICENSE](LICENSE).
