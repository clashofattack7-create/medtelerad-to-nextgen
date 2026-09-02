import re, os
BASE = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(BASE, 'mt_after_login.html'), encoding='utf-8', errors='replace').read()

def around(kw, width=500, maxh=6):
    print(f'\n--- "{kw}" ---')
    for i in [m.start() for m in re.finditer(re.escape(kw), html, re.I)][:maxh]:
        print(html[max(0, i-250):i+width].replace('\n', ' '))
        print('-' * 70)

around('today')
around('download')

print('\n=== input controls ===')
for m in re.finditer(r'<input[^>]*>', html):
    tag = m.group(0)
    nm = re.search(r'name="([^"]*)"', tag)
    ty = re.search(r'type="([^"]*)"', tag)
    idd = re.search(r'id="([^"]*)"', tag)
    vl = re.search(r'value="([^"]*)"', tag)
    print(f'name={nm.group(1) if nm else "-":30s} type={ty.group(1) if ty else "-":10s} id={idd.group(1) if idd else "-":30s} value={(vl.group(1) if vl else "")[:40]}')

print('\n=== select controls ===')
for m in re.finditer(r'<select[^>]*>', html):
    print(m.group(0)[:140])

print('\n=== buttons ===')
for m in re.finditer(r'<input[^>]*type="(?:submit|button)"[^>]*>', html):
    print(m.group(0)[:160])

print('\n=== report link sample (lnkRpt) context ===')
i = html.find('lnkRpt')
print(html[max(0, i-400):i+400].replace('\n', ' '))
