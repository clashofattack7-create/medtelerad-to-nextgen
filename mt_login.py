import urllib.request, urllib.parse, http.cookiejar, re, os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(BASE_DIR, 'config.json'), encoding='utf-8'))
USER = cfg['medtelerad']['user']
PASS = cfg['medtelerad']['pass']
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

# GET login page
r = opener.open(BASE + '/user/Login.aspx', timeout=25)
html = r.read().decode('utf-8', 'replace')
print('login GET final url:', r.geturl())

data = urllib.parse.urlencode({
    '__LASTFOCUS': '',
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': hidden(html, '__VIEWSTATE'),
    '__VIEWSTATEGENERATOR': hidden(html, '__VIEWSTATEGENERATOR'),
    '__EVENTVALIDATION': hidden(html, '__EVENTVALIDATION'),
    'txtUser': USER,
    'txtPassword': PASS,
    'btnLogin': 'LOGIN',
}).encode()

req = urllib.request.Request(BASE + '/user/Login.aspx', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
req.add_header('Referer', BASE + '/user/Login.aspx')

try:
    resp = opener.open(req, timeout=25)
    body = resp.read().decode('utf-8', 'replace')
    with open(os.path.join(BASE_DIR, 'mt_after_login.html'), 'w', encoding='utf-8') as f:
        f.write(body)
    print('login POST status:', resp.status)
    print('login POST final url:', resp.geturl())
    print('body length:', len(body))
    if 'login.aspx' in resp.geturl().lower():
        print('>> STILL ON LOGIN PAGE (likely failed)')
        for m in re.finditer(r'(?i)(invalid|incorrect|wrong|error|failed|not match)[^<]{0,100}', body):
            print('   hint:', m.group(0)[:120])
    else:
        print('>> REDIRECTED (likely success) ->', resp.geturl())
except urllib.error.HTTPError as e:
    print('HTTPError', e.code, '|', e.geturl())
except Exception as e:
    print('err:', repr(e))
