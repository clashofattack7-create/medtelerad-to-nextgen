import re, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nextgen_assets')
files = ['main.9182d5c6c2944413c6f0.js', 'scripts.7a03926cf12412c6580c.js']

# string literals containing interesting keywords
pat = re.compile(r'["\']([^"\']*(?:login|Login|upload|Upload|authenticate|auth|token|Token|api|controller|Controller|multipart|attachment|report|Report|file)[^"\']*)["\']')
seen = set()
for f in files:
    data = open(os.path.join(OUT, f), encoding='utf-8', errors='replace').read()
    for m in pat.finditer(data):
        s = m.group(1).strip()
        if 2 < len(s) < 140 and s not in seen:
            seen.add(s)
            print(f, '::', s)
