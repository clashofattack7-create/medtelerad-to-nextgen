import base64, urllib.request, json, ssl

BASE = 'https://nextgen.ehospital.gov.in'
ctx = ssl.create_default_context()
r = urllib.request.Request(BASE + '/api/authentication/v1/pubkey', headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'})
with urllib.request.urlopen(r, timeout=30, context=ctx) as resp:
    pub = json.loads(resp.read())
pk = pub['result']['public_key']
der = base64.b64decode(pk)
print('DER len:', len(der))
print('DER first 24 bytes:', der[:24].hex())

NAMES = {0x30: 'SEQUENCE', 0x02: 'INTEGER', 0x03: 'BIT STRING', 0x06: 'OID', 0x05: 'NULL', 0x04: 'OCTET STRING', 0x01: 'BOOLEAN'}

def dump(data, off=0, depth=0, maxdepth=5):
    if off >= len(data):
        return off
    tag = data[off]; off += 1
    ln = data[off]; off += 1
    if ln & 0x80:
        nb = ln & 0x7f
        ln = int.from_bytes(data[off:off+nb], 'big')
        off += nb
    val = data[off:off+ln]
    end = off + ln
    name = NAMES.get(tag, f'TAG0x{tag:02x}')
    extra = ''
    if tag == 0x02:
        extra = f' value={int.from_bytes(val, "big") if len(val) <= 8 else "(big)"}'
    if tag == 0x06:
        extra = f' oid={val.hex()}'
    print('  ' * depth + f'{name} len={ln}{extra} head={val[:8].hex()}')
    if depth < maxdepth:
        if tag == 0x30:
            o = 0
            while o < len(val):
                o = dump(val, o, depth + 1, maxdepth)
        elif tag == 0x03:
            inner = val[1:] if val else val
            print('  ' * (depth + 1) + f'[BIT STRING inner] head={inner[:8].hex()}')
            dump(inner, 0, depth + 1, maxdepth)
    return end

dump(der)
