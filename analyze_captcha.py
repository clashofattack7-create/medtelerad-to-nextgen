from PIL import Image
from collections import Counter
import sys

img = Image.open(sys.argv[1]).convert('RGB')
print('size:', img.size)
pix = list(img.getdata())
print('total px:', len(pix))
c = Counter(pix)
print('unique colors:', len(c))
for col, n in c.most_common(12):
    print(f'  {col} -> {n}')

lum = Counter()
for r, g, b in pix:
    lum[(r + g + b) // 3] += 1
print('luminance histogram (top bins):')
for v, n in sorted(lum.items(), key=lambda x: -x[1])[:14]:
    print(f'  lum {v} -> {n}')
