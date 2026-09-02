import re, os
BASE = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(BASE, 'mt_after_login.html'), encoding='utf-8', errors='replace').read()
print('length:', len(html))

m = re.search(r'<title>(.*?)</title>', html, re.S | re.I)
print('title:', m.group(1).strip() if m else None)

print('\n--- links (href => text) ---')
for a in re.finditer(r'<a\b[^>]*>.*?</a>', html, re.S | re.I):
    tag = a.group(0)
    href = re.search(r'href="([^"]*)"', tag)
    text = re.sub(r'<[^>]+>', ' ', tag)
    text = re.sub(r'\s+', ' ', text).strip()
    if href or text:
        print(f'{(href.group(1) if href else "-"):60s} => {text[:70]}')

print('\n--- iframes ---')
for f in re.finditer(r'<iframe[^>]*src="([^"]*)"', html, re.I):
    print(f.group(1))

print('\n--- forms ---')
for f in re.finditer(r'<form[^>]*>', html, re.I):
    print(f.group(0)[:200])

print('\n--- __doPostBack targets ---')
for d in re.finditer(r'__doPostBack\s*\(\s*[\'"]([^\'"]+)[\'"]', html):
    print(d.group(1))

print('\n--- keyword counts ---')
for kw in ['report', 'download', 'today', 'upload', 'view', 'search', 'date', 'patient', 'list']:
    print(f'{kw}: {len(re.findall(kw, html, re.I))}')
