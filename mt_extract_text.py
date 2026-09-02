import urllib.request, urllib.parse, http.cookiejar, re, os, json, html as ihtml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(BASE_DIR, 'config.json'), encoding='utf-8'))
BASE = cfg['medtelerad']['base']

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]

def hidden(html, name):
    m = re.search(r'<input[^>]*name="' + re.escape(name) + r'"[^>]*>', html)
    if not m:
        return ''
    v = re.search(r'value="([^"]*)"', m.group(0))
    return v.group(1) if v else ''

r = opener.open(BASE + '/user/Login.aspx', timeout=25)
html = r.read().decode('utf-8', 'replace')
data = urllib.parse.urlencode({
    '__VIEWSTATE': hidden(html, '__VIEWSTATE'),
    '__VIEWSTATEGENERATOR': hidden(html, '__VIEWSTATEGENERATOR'),
    '__EVENTVALIDATION': hidden(html, '__EVENTVALIDATION'),
    'txtUser': cfg['medtelerad']['user'], 'txtPassword': cfg['medtelerad']['pass'], 'btnLogin': 'LOGIN',
}).encode()
req = urllib.request.Request(BASE + '/user/Login.aspx', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
resp = opener.open(req, timeout=25)
dash = resp.read().decode('utf-8', 'replace')

suids = re.findall(r'name="gvTest\$ctl\d+\$stUID"[^>]*value="([^"]+)"', dash)
ptids = re.findall(r'name="gvTest\$ctl\d+\$ptID"[^>]*value="([^"]+)"', dash)
# fetch PATIENT_F (index 16) which is a confirmed RIS match
suid = suids[16]
print('Fetching PATIENT_F  report, ptID=', ptids[16])
url = BASE + '/report/FinalizedReport.aspx?UID=' + urllib.parse.quote(suid) + '&user=' + cfg['medtelerad']['user']
rr = opener.open(url, timeout=40)
rhtml = rr.read().decode('utf-8', 'replace')

m = re.search(r'<textarea id="txtTemplate1"[^>]*>(.*?)</textarea>', rhtml, re.S)
content = ihtml.unescape(m.group(1)) if m else ''

# strip XML comments and <xml>...</xml> blocks
content2 = re.sub(r'<!--.*?-->', '', content, flags=re.S)
content2 = re.sub(r'<xml>.*?</xml>', '', content2, flags=re.S)

# save raw + cleaned
open(os.path.join(BASE_DIR, 'mt_report_raw.html'), 'w', encoding='utf-8').write(content)
open(os.path.join(BASE_DIR, 'mt_report_clean.html'), 'w', encoding='utf-8').write(content2)

# strip all tags -> plain text
plain = re.sub(r'<[^>]+>', '\n', content2)
plain = re.sub(r'\n\s*\n+', '\n', plain)
plain = re.sub(r'[ \t]+', ' ', plain)
print('--- CLEANED PLAIN TEXT ---')
print(plain[:4000])
