const tls = require('tls');
const http = require('http');

function tlsProbe(host, port, options, label) {
  return new Promise((resolve) => {
    const opts = Object.assign({ host, port, rejectUnauthorized: false }, options);
    let settled = false;
    const s = tls.connect(opts, () => {
      settled = true;
      const cert = s.getPeerCertificate();
      resolve({
        label, connected: true,
        authorized: s.authorized,
        protocol: s.getProtocol(),
        cipher: s.getCipher() ? s.getCipher().name : null,
        certCN: cert && cert.subject ? cert.subject.CN : null,
        certIssuer: cert && cert.issuer ? cert.issuer.CN : null,
        certValidFrom: cert && cert.valid_from,
        certValidTo: cert && cert.valid_to,
      });
      s.end();
    });
    s.on('error', (e) => { if (!settled) { settled = true; resolve({ label, connected: false, error: e.message }); } });
    s.setTimeout(15000, () => { if (!settled) { settled = true; s.destroy(); resolve({ label, connected: false, error: 'timeout' }); } });
  });
}

(async () => {
  const host = 'nextgen.ehospital.gov.in';
  const cases = [
    [{}, 'default TLS'],
    [{ minVersion: 'TLSv1' }, 'minVersion=TLSv1'],
    [{ minVersion: 'TLSv1', maxVersion: 'TLSv1' }, 'TLSv1 only'],
    [{ minVersion: 'TLSv1.1', maxVersion: 'TLSv1.1' }, 'TLSv1.1 only'],
  ];
  for (const [opts, label] of cases) {
    console.log(JSON.stringify(await tlsProbe(host, 443, opts, label)));
  }

  console.log('\n--- plain HTTP :80 ---');
  const req = http.get('http://' + host + '/', (res) => {
    console.log('http status:', res.statusCode, '| location:', res.headers.location);
    res.resume();
    res.on('end', () => process.exit(0));
  });
  req.on('error', (e) => { console.log('http error:', e.message); process.exit(0); });
  req.setTimeout(10000, () => { req.destroy(); console.log('http timeout'); process.exit(0); });
})();
