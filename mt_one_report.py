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
resp = opener.open(req, timeout=25)
dash = resp.read().decode('utf-8', 'replace')

suids = re.findall(r'name="gvTest\$ctl\d+\$stUID"[^>]*value="([^"]+)"', dash)
ptids = re.findall(r'name="gvTest\$ctl\d+\$ptID"[^>]*value="([^"]+)"', dash)
ptnames = re.findall(r'name="gvTest\$ctl\d+\$ptName"[^>]*value="([^"]+)"', dash)
rpt_statuses = [m.group(1).strip() for m in re.finditer(r'__doPostBack\(&#39;gvTest\$ctl\d+\$lnkRpt&#39;,&#39;&#39;\)[^>]*>([^<]*)<', dash)]

print('counts: suids=%d ptids=%d ptnames=%d statuses=%d' % (len(suids), len(ptids), len(ptnames), len(rpt_statuses)))
for i in range(len(suids)):
    nm = ptnames[i] if i < len(ptnames) else '?'
    pid = ptids[i] if i < len(ptids) else '?'
    st = rpt_statuses[i] if i < len(rpt_statuses) else '?'
    print(f'{i:2d}: {nm:22s} | {pid:16s} | {st}')

idx = next((i for i, s in enumerate(rpt_statuses) if s == 'Final'), 0)
suid = suids[idx]
print(f'\n>>> Fetching Final report: {ptnames[idx]} ({ptids[idx]})')
url = BASE + '/report/FinalizedReport.aspx?UID=' + urllib.parse.quote(suid) + '&user=' + cfg['medtelerad']['user']
rr = opener.open(url, timeout=40)
rhtml = rr.read().decode('utf-8', 'replace')

def span(html, sid):
    m = re.search(r'id="' + sid + r'"[^>]*>([^<]*)<', html)
    return m.group(1).strip() if m else ''

print('lblPatName:', span(rhtml, 'lblPatName'))
print('lblPatID:', span(rhtml, 'lblPatID'))
print('lblStudy:', span(rhtml, 'lblStudy'))
print('lblMod:', span(rhtml, 'lblMod'))
m = re.search(r'<textarea id="txtTemplate1"[^>]*>(.*?)</textarea>', rhtml, re.S)
if m:
    content = m.group(1)
    print('textarea len:', len(content))
    print('--- textarea content (first 4000 chars) ---')
    print(content[:4000])
