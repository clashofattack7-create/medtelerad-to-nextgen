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

def hidden_fields(html):
    d = {}
    for name in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION',
                 '__EVENTTARGET', '__EVENTARGUMENT', '__LASTFOCUS']:
        d[name] = hidden(html, name)
    return d

# login
r = opener.open(BASE + '/user/Login.aspx', timeout=25)
html = r.read().decode('utf-8', 'replace')
data = urllib.parse.urlencode({**hidden_fields(html),
    'txtUser': cfg['medtelerad']['user'],
    'txtPassword': cfg['medtelerad']['pass'],
    'btnLogin': 'LOGIN'}).encode()
req = urllib.request.Request(BASE + '/user/Login.aspx', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
resp = opener.open(req, timeout=25)
dash = resp.read().decode('utf-8', 'replace')
print('login ok ->', resp.geturl())

suids = re.findall(r'name="gvTest\$ctl\d+\$stUID"[^>]*value="([^"]+)"', dash)
suid = suids[0]
url = BASE + '/report/FinalizedReport.aspx?UID=' + urllib.parse.quote(suid) + '&user=' + cfg['medtelerad']['user']

# GET report page
rr = opener.open(url, timeout=40)
rhtml = rr.read().decode('utf-8', 'replace')
print('report page bytes:', len(rhtml))

# POST btnPdf (Download in PDF)
fields = hidden_fields(rhtml)
fields['btnPdf'] = 'Download in PDF'
data = urllib.parse.urlencode(fields).encode()
req = urllib.request.Request(url, data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
req.add_header('Referer', url)
try:
    pr = opener.open(req, timeout=90)
    body = pr.read()
    ct = pr.headers.get('Content-Type', '')
    cd = pr.headers.get('Content-Disposition', '')
    print('pdf postback status:', pr.status)
    print('Content-Type:', ct)
    print('Content-Disposition:', cd)
    print('bytes:', len(body))
    if body[:4] == b'%PDF':
        with open(os.path.join(BASE_DIR, 'sample_report.pdf'), 'wb') as f:
            f.write(body)
        print('SAVED sample_report.pdf')
    else:
        print('head:', body[:400].decode('utf-8', 'replace').replace('\n', ' '))
except urllib.error.HTTPError as e:
    print('HTTPError', e.code)
except Exception as e:
    print('err:', repr(e))
