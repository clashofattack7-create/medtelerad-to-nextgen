// Connectivity probe: MedTelerad (http) + NextGen (https via Node/OpenSSL)
const http = require('http');
const https = require('https');
const url = require('url');

function httpGet(u) {
  return new Promise((resolve) => {
    const req = http.get(u, (res) => {
      let body = '';
      res.on('data', (c) => body += c);
      res.on('end', () => resolve({ status: res.statusCode, finalUrl: u, body }));
    });
    req.on('error', (e) => resolve({ status: 'ERR', body: e.message }));
    req.setTimeout(20000, () => req.destroy(new Error('timeout')));
  });
}

function httpsGet(u) {
  return new Promise((resolve) => {
    const opts = url.parse(u);
    opts.rejectUnauthorized = false; // diagnostic only
    const req = https.get(opts, (res) => {
      let body = '';
      res.on('data', (c) => body += c);
      res.on('end', () => {
        const cert = res.socket.getPeerCertificate();
        resolve({ status: res.statusCode, finalUrl: u, body,
          certSubject: cert && cert.subject ? cert.subject.CN : null,
          tlsVersion: res.socket.getProtocol ? res.socket.getProtocol() : null });
      });
    });
    req.on('error', (e) => resolve({ status: 'ERR', body: e.message }));
    req.setTimeout(20000, () => req.destroy(new Error('timeout')));
  });
}

(async () => {
  console.log('=== MedTelerad login page (http) ===');
  const mt = await httpGet('http://tele.medtelerad.com/user/Login.aspx');
  console.log('status:', mt.status, '| body length:', mt.body.length);

  console.log('\n=== NextGen adminHome (https) ===');
  const ng = await httpsGet('https://nextgen.ehospital.gov.in/adminHome');
  console.log('status:', ng.status);
  console.log('cert CN:', ng.certSubject, '| tls:', ng.tlsVersion);
  console.log('body length:', ng.body.length);
  console.log('body head:', ng.body.slice(0, 300).replace(/\s+/g, ' '));
})();
