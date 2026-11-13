import http.server, socketserver, os, sys
os.chdir(os.path.join(os.getcwd(),'web'))
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
with S(('127.0.0.1', 8123), H) as httpd:
    print('serving 8123 threaded')
    httpd.serve_forever()
