import re, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ris_assets')
data = open(os.path.join(OUT, 'main.1f4297bd0d1e0d82fe5a.js'), encoding='utf-8', errors='replace').read()

# print the full environment object (the "const i=window.env.baseURL,r={...}" block)
m = re.search(r'const i=window\.env\.baseURL', data)
if m:
    seg = data[m.start():m.start()+2500]
    print(seg.replace('\n', ' '))
