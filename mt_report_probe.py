import urllib.request, urllib.parse, http.cookiejar, re, os, json

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

# login
r = opener.open(BASE + '/user/Login.aspx', timeout=25)
html = r.read().decode('utf-8', 'replace')
data = urllib.parse.urlencode({
    '__VIEWSTATE': hidden(html, '__VIEWSTATE'),
    '__VIEWSTATEGENERATOR': hidden(html, '__VIEWSTATEGENERATOR'),
    '__EVENTVALIDATION': hidden(html, '__EVENTVALIDATION'),
    'txtUser': cfg['medtelerad']['user'],
    'txtPassword': cfg['medtelerad']['pass'],
    'btnLogin': 'LOGIN',
}).encode()
req = urllib.request.Request(BASE + '/user/Login.aspx', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
req.add_header('Referer', BASE + '/user/Login.aspx')
resp = opener.open(req, timeout=25)
dash = resp.read().decode('utf-8', 'replace')
print('login final url:', resp.geturl())

# lblUser
usr = 'UNKNOWN'
m = re.search(r'id="lblUser"[^>]*>([^<]*)<', dash)
if m:
    usr = m.group(1).strip()
else:
    m = re.search(r'id="lblUser"[^>]*value="([^"]*)"', dash)
    if m:
        usr = m.group(1)
print('lblUser:', usr)

suids = re.findall(r'name="gvTest\$ctl\d+\$stUID"[^>]*value="([^"]+)"', dash)
print('num studies on page:', len(suids))

if suids:
    url = BASE + '/report/FinalizedReport.aspx?UID=' + urllib.parse.quote(suids[0]) + '&user=' + urllib.parse.quote(usr)
    print('fetching:', url)
    try:
        rr = opener.open(url, timeout=40)
        body = rr.read()
        ct = rr.headers.get('Content-Type', '')
        print('status:', rr.status, '| content-type:', ct, '| bytes:', len(body))
        ext = '.pdf' if 'pdf' in ct.lower() else '.html'
        with open(os.path.join(BASE_DIR, 'sample_report' + ext), 'wb') as f:
            f.write(body)
        print('saved sample_report' + ext)
        txt = body.decode('utf-8', 'replace')
        head = txt[:400].replace('\n', ' ')
        print('head:', head if not txt.startswith('%PDF') else '(PDF starts)')
        for kw in ['Print', 'print', 'Download', 'download', 'iframe', 'ReportViewer', 'pdf', 'PDF', 'Crystal', 'report']:
            c = txt.count(kw)
            if c:
                print(f'  keyword "{kw}": {c}')
    except Exception as e:
        print('err:', repr(e))
