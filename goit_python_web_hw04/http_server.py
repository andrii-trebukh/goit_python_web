from http.server import BaseHTTPRequestHandler, HTTPServer
import mimetypes
from pathlib import Path
import pickle
import socket
import sys
import urllib.parse

HTML_PATH = "./html"


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        url_path = url.path[1:] if url.path != "/" else "index.html"
        path = Path(HTML_PATH).joinpath(url_path)

        mt = mimetypes.guess_type(self.path)[0]
        if mt is None:
            mt = "text/html"

        if path.exists():
            self.send_html_file(path, filetype=mt)
        else:
            self.send_html_file(path.parent.joinpath("error.html"), status=404)

    def send_html_file(self, filename, status=200, filetype="text/html"):
        self.send_response(status)
        self.send_header('Content-type', filetype)
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = dict([el.split('=') for el in data_parse.split('&')])
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        socket_send(data_dict)


def socket_send(data: dict, ip: str = "127.0.0.1", port: int = 5000):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(pickle.dumps(data), (ip, port))
    sock.close()


def httpd_run(
        server_class=HTTPServer,
        handler_class=HTTPRequestHandler,
        host="",
        port=8000
        ):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Destroy http server')
    finally:
        httpd.server_close()
        sys.exit(0)
