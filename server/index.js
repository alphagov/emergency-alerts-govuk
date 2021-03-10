const http2 = require('http2');
const fs = require('fs');

const PORT = 8443;
const indexPage = fs.readFileSync('./dist/index.html');

const server = http2.createSecureServer({
  key: fs.readFileSync('./server/localhost-privkey.pem'),
  cert: fs.readFileSync('./server/localhost-cert.pem')
});
server.on('error', (err) => console.error(err));

server.on('stream', (stream, headers) => {
  const method = headers[':method'];
  const path = headers[':path'];
  const contentType = headers['accept'].split(',')[0];

  console.log(`${method} request for ${path}`);

  // stream is a Duplex
  stream.respond({
    'content-type': `${contentType}; charset=utf-8`,
    ':status': 200
  });

  if (path === '/') {
    stream.end(indexPage);
  } else if (/^\/alerts\/assets/.test(path)){
    stream.end(fs.readFileSync(`./dist${path.split('?')[0]}`));
  } else {
    stream.end('<!DOCTYPE html><html><head><meta charset="utf-8"><title>Default page</title></head><body><h1>Default page</h1></body></html>');
  }
});

server.listen(PORT);
console.log(`HTTP2 server running at https://localhost:${PORT}`);
