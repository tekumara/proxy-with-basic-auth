#!/usr/bin/env python3

import http.server
import socketserver
import base64
import http.client
import shutil
import urllib.parse

basic = lambda u, p: 'Basic %s' % base64.b64encode(('%s:%s' % (u, p)).encode())

AUTHORIZATIONS = {
    'maven.initech.com': basic('aladdin', 'opensesame'),
    'maven.vendoro.com': basic('aladdin', 'opensesame'),
    'localhost:5000': basic('aladdin', 'opensesame'),
}


class Handler(http.server.BaseHTTPRequestHandler):
  def go(self):
    ru = urllib.parse.urlparse(self.path)
    pu = urllib.parse.ParseResult('', '', ru.path, ru.params, ru.query, ru.fragment)
    auth = AUTHORIZATIONS.get(str(ru.netloc))
    if auth:
      self.headers['Authorization'] = auth
    self.headers['Host'] = ru.netloc
    if ru.scheme == 'https':
      c = http.client.HTTPSConnection(ru.netloc)
    else:
      c = http.client.HTTPConnection(ru.netloc)
    try:
      c.putrequest(self.command, pu.geturl())
      for k, v in list(self.headers.items()):
        c.putheader(k, v)
      c.endheaders()
      r = c.getresponse()
      self.send_response(r.status)
      for k, v in r.getheaders():
        self.send_header(k, v)
      self.end_headers()
      shutil.copyfileobj(r, self.wfile)
      self.wfile.flush()
    finally:
      c.close()

  do_GET = go
  do_HEAD = go


class ThreadedHTTPServer(socketserver.ThreadingMixIn,
                         http.server.HTTPServer):
  daemon_threads = True


ThreadedHTTPServer(('', 4000), Handler).serve_forever()