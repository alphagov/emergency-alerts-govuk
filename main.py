import http.server
import os

PORT = 8000

web_dir = os.path.join(os.path.dirname(__file__), 'dist')
os.chdir(web_dir)

Handler = http.server.SimpleHTTPRequestHandler

Handler.extensions_map = {
    '': 'text/html',
    '.css': 'text/css'
}

httpd = http.server.HTTPServer(("", PORT), Handler)

print("serving at port", PORT)
httpd.serve_forever()
