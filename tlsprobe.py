import ssl, socket

host = 'nextgen.ehospital.gov.in'
port = 443

tests = [
    ('TLSv1.3', ssl.TLSVersion.TLSv1_3, ssl.TLSVersion.TLSv1_3),
    ('TLSv1.2', ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_2),
    ('TLSv1.1', ssl.TLSVersion.TLSv1_1, ssl.TLSVersion.TLSv1_1),
    ('TLSv1',   ssl.TLSVersion.TLSv1,   ssl.TLSVersion.TLSv1),
]

for label, mn, mx in tests:
    try:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            ctx.set_ciphers('ALL:@SECLEVEL=0')
        except Exception:
            pass
        try:
            ctx.minimum_version = mn
            ctx.maximum_version = mx
        except Exception as e:
            print(label, '| version-set err:', e)
            continue
        s = socket.create_connection((host, port), timeout=12)
        try:
            ss = ctx.wrap_socket(s, server_hostname=host)
            print(label, '| OK |', ss.version(), '|', ss.cipher())
            ss.close()
        except Exception as e:
            print(label, '| wrap err:', repr(e))
        finally:
            try: s.close()
            except Exception: pass
    except Exception as e:
        print(label, '| conn err:', repr(e))
