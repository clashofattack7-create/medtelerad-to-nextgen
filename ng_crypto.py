"""
Pure-python crypto needed for NextGen eHospital:
  - RSA PKCS#1 v1.5 encryption (jsencrypt-compatible)
  - AES-128 ECB encrypt/decrypt (CryptoJS-compatible, PKCS7 padding)
No third-party libs required.
"""
import base64
import os

# ----------------------------------------------------------------------------
# AES-128 (ECB)
# ----------------------------------------------------------------------------
SBOX = [
0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16,
]
INV_SBOX = [0] * 256
for _i, _v in enumerate(SBOX):
    INV_SBOX[_v] = _i

RCON = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d,0x9a]

def _gmul(a, b):
    r = 0
    for _ in range(8):
        if b & 1:
            r ^= a
        hi = a & 0x80
        a = (a << 1) & 0xff
        if hi:
            a ^= 0x1b
        b >>= 1
    return r

def _key_expansion(key16):
    w = [list(key16[i*4:i*4+4]) for i in range(4)]
    for i in range(4, 44):
        temp = list(w[i-1])
        if i % 4 == 0:
            temp = temp[1:] + temp[:1]
            temp = [SBOX[b] for b in temp]
            temp[0] ^= RCON[i//4 - 1]
        w.append([w[i-4][j] ^ temp[j] for j in range(4)])
    return [[b for word in w[r*4:r*4+4] for b in word] for r in range(11)]

def _add_round_key(s, rk):
    return [s[i] ^ rk[i] for i in range(16)]

def _sub_bytes(s):
    return [SBOX[b] for b in s]

def _inv_sub_bytes(s):
    return [INV_SBOX[b] for b in s]

def _shift_rows(s):
    o = [0]*16
    for r in range(4):
        for c in range(4):
            o[4*c + r] = s[4*((c + r) % 4) + r]
    return o

def _inv_shift_rows(s):
    o = [0]*16
    for r in range(4):
        for c in range(4):
            o[4*c + r] = s[4*((c - r) % 4) + r]
    return o

def _mix_columns(s):
    o = [0]*16
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        o[4*c]   = _gmul(a0,2) ^ _gmul(a1,3) ^ a2 ^ a3
        o[4*c+1] = a0 ^ _gmul(a1,2) ^ _gmul(a2,3) ^ a3
        o[4*c+2] = a0 ^ a1 ^ _gmul(a2,2) ^ _gmul(a3,3)
        o[4*c+3] = _gmul(a0,3) ^ a1 ^ a2 ^ _gmul(a3,2)
    return o

def _inv_mix_columns(s):
    o = [0]*16
    for c in range(4):
        a0, a1, a2, a3 = s[4*c], s[4*c+1], s[4*c+2], s[4*c+3]
        o[4*c]   = _gmul(a0,14) ^ _gmul(a1,11) ^ _gmul(a2,13) ^ _gmul(a3,9)
        o[4*c+1] = _gmul(a0,9)  ^ _gmul(a1,14) ^ _gmul(a2,11) ^ _gmul(a3,13)
        o[4*c+2] = _gmul(a0,13) ^ _gmul(a1,9)  ^ _gmul(a2,14) ^ _gmul(a3,11)
        o[4*c+3] = _gmul(a0,11) ^ _gmul(a1,13) ^ _gmul(a2,9)  ^ _gmul(a3,14)
    return o

def _aes_encrypt_block(block16, rk):
    s = _add_round_key(list(block16), rk[0])
    for r in range(1, 10):
        s = _sub_bytes(s); s = _shift_rows(s); s = _mix_columns(s)
        s = _add_round_key(s, rk[r])
    s = _sub_bytes(s); s = _shift_rows(s); s = _add_round_key(s, rk[10])
    return bytes(s)

def _aes_decrypt_block(block16, rk):
    s = _add_round_key(list(block16), rk[10])
    for r in range(9, 0, -1):
        s = _inv_shift_rows(s); s = _inv_sub_bytes(s)
        s = _add_round_key(s, rk[r]); s = _inv_mix_columns(s)
    s = _inv_shift_rows(s); s = _inv_sub_bytes(s); s = _add_round_key(s, rk[0])
    return bytes(s)

def aes128_ecb_encrypt(key16, plaintext):
    rk = _key_expansion(key16)
    pad = 16 - (len(plaintext) % 16)
    data = plaintext + bytes([pad]) * pad
    out = b''
    for i in range(0, len(data), 16):
        out += _aes_encrypt_block(data[i:i+16], rk)
    return out

def aes128_ecb_decrypt(key16, ciphertext):
    rk = _key_expansion(key16)
    out = b''
    for i in range(0, len(ciphertext), 16):
        out += _aes_decrypt_block(ciphertext[i:i+16], rk)
    pad = out[-1]
    if 1 <= pad <= 16:
        out = out[:-pad]
    return out

# ----------------------------------------------------------------------------
# Minimal DER reader + RSA PKCS#1 v1.5 encryption
# ----------------------------------------------------------------------------
def _read_tlv(data, off):
    tag = data[off]; off += 1
    ln = data[off]; off += 1
    if ln & 0x80:
        nb = ln & 0x7f
        ln = int.from_bytes(data[off:off+nb], 'big')
        off += nb
    return tag, data[off:off+ln], off + ln

def parse_rsa_public_key(der):
    """Return (n, e) from a DER SPKI or PKCS#1 RSAPublicKey."""
    tag, outer, _ = _read_tlv(der, 0)          # outer SEQUENCE
    tag1, val1, off = _read_tlv(outer, 0)
    if tag1 == 0x30:
        # SPKI: SEQUENCE { AlgorithmIdentifier SEQUENCE, BIT STRING { RSAPublicKey } }
        tag2, bitstr, off = _read_tlv(outer, off)
        if bitstr and bitstr[0] == 0:
            bitstr = bitstr[1:]                 # strip unused-bits-count byte
        _, rsa, _ = _read_tlv(bitstr, 0)        # unwrap RSAPublicKey SEQUENCE -> its content
    else:
        # PKCS#1: outer is already SEQUENCE { INTEGER n, INTEGER e }
        rsa = outer
    tag_n, n_bytes, off = _read_tlv(rsa, 0)
    tag_e, e_bytes, _ = _read_tlv(rsa, off)
    n = int.from_bytes(n_bytes, 'big')
    e = int.from_bytes(e_bytes, 'big')
    return n, e

def rsa_encrypt_pkcs1_v15(pubkey_b64, message_bytes):
    n, e = parse_rsa_public_key(base64.b64decode(pubkey_b64))
    k = (n.bit_length() + 7) // 8
    if len(message_bytes) > k - 11:
        raise ValueError('message too long for RSA key')
    ps = os.urandom(k - len(message_bytes) - 3)
    ps = bytes(b if b != 0 else 0x01 for b in ps)
    em = b'\x00\x02' + ps + b'\x00' + message_bytes
    m = int.from_bytes(em, 'big')
    c = pow(m, e, n)
    return base64.b64encode(c.to_bytes(k, 'big')).decode()

# ----------------------------------------------------------------------------
# Self-tests
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    # AES-128 FIPS-197 known answer test
    key = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
    pt = bytes.fromhex('00112233445566778899aabbccddeeff')
    ct_expected = '69c4e0d86a7b0430d8cdb78070b4c55a'
    ct = aes128_ecb_encrypt(key, pt)
    print('AES KAT:', 'PASS' if ct[:16].hex() == ct_expected else f'FAIL got {ct.hex()}')
    # round-trip with padding
    msg = b'{"access_token":"abc","projects_list":[],"health_facility_id":1}'
    enc = aes128_ecb_encrypt(key, msg)
    dec = aes128_ecb_decrypt(key, enc)
    print('AES roundtrip:', 'PASS' if dec == msg else f'FAIL {dec!r}')
    print('ALL DONE')
