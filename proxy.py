import BaseHTTPServer
import SocketServer
import base64
import httplib
import shutil
import urlparse

basic = lambda u,p: 'Basic %s' % base64.b64encode('%s:%s' % (u,p))

AUTHORIZATIONS = {
    'maven.initech.com': basic('aladdin', 'opensesame'),
    'maven.vendoro.com': basic('aladdin', 'opensesame'),
    'localhost:5000': basic('aladdin', 'opensesame'),
}

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
  def go(self):
    ru = urlparse.urlparse(self.path)
    pu = urlparse.ParseResult('', '', ru.path, ru.params, ru.query, ru.fragment)
    auth = AUTHORIZATIONS.get(str(ru.netloc))
    if auth:
      self.headers['Authorization'] = auth
    self.headers['Host'] = ru.netloc
    if ru.scheme == 'https':
      c = httplib.HTTPSConnection(ru.netloc)
    else:
      c = httplib.HTTPConnection(ru.netloc)
    try:
      c.putrequest(self.command, pu.geturl())
      for k, v in self.headers.items():
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

class ThreadedHTTPServer(SocketServer.ThreadingMixIn,
                         BaseHTTPServer.HTTPServer):
  daemon_threads = True

ThreadedHTTPServer(('', 4000), Handler).serve_forever()
