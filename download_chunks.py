import re, os, json, urllib.request, ssl

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
runtime = open(os.path.join(OUT, 'runtime.00f768e16c5eec97da6e.js'), encoding='utf-8', errors='replace').read()

# extract the two objects in u.src = function(e){ return a.p+""+({...}[e]||e)+"."+({...}[e])+".js" }
m = re.search(r'u\.src=function\(e\)\{return a\.p\+""\+(\{[^}]*\})\|?\|?e?\)?\+"\."\+(\{[^}]*\})\[e\]\+"\.js"', runtime)
# simpler: find the chunk name map and hash map
name_map_str = re.search(r'\(\{0:"common",.*?\}\)\[e\]', runtime)
hash_map_str = re.search(r'\.\{0:"[0-9a-f]+".*?\}\[e\]', runtime)

# fallback: extract raw dicts
def extract_dict(runtime, start_marker):
    i = runtime.find(start_marker)
    if i < 0:
        return None
    # find the matching braces
    depth = 0
    for j in range(i, len(runtime)):
        if runtime[j] == '{':
            depth += 1
        elif runtime[j] == '}':
            depth -= 1
            if depth == 0:
                return runtime[i:j+1]
    return None

name_d = extract_dict(runtime, '{0:"common"')
hash_d = extract_dict(runtime, '.{0:"')

if name_d is None or hash_d is None:
    print('could not extract chunk maps')
    print(runtime[:2000])
    raise SystemExit

# parse the JS dicts into python (replace keys, use json-ish)
import re as _re
def parse_js_dict(s):
    s = s.strip().lstrip('.').strip('{').rstrip('}')
    out = {}
    for m in _re.finditer(r'(\d+):"([^"]*)"', s):
        out[int(m.group(1))] = m.group(2)
    return out

names = parse_js_dict(name_d)
hashes = parse_js_dict(hash_d)
print('chunks found:')
for k in sorted(names):
    print(f'  {k}: {names[k]}')

BASE = 'https://nextgen.ehospital.gov.in/ris/'
ctx = ssl.create_default_context()

def fetch(url):
    r = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(r, timeout=60, context=ctx) as resp:
        return resp.read()

for cid in [10, 11]:
    fname = names[cid] + '.' + hashes[cid] + '.js'
    url = BASE + fname
    print(f'\ndownloading {fname} ...')
    try:
        data = fetch(url)
        open(os.path.join(OUT, fname), 'wb').write(data)
        print(f'saved {len(data)} bytes')
    except Exception as e:
        print('ERR', repr(e))
