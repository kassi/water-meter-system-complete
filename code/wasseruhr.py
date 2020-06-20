from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import lib.ZaehlerstandClass
import os
import subprocess

import socketserver

import gc

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global wasserzaehler
        url_parse = parse.urlparse(self.path)
        query_parse = parse.parse_qs(url_parse.query)

        if 'reload' in url_parse.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            result = 'Konfiguration wird neu geladen'
            self.wfile.write(bytes(result, 'UTF-8'))
            del wasserzaehler
            gc.collect()
            wasserzaehler = lib.ZaehlerstandClass.Zaehlerstand()
            return

        if ('version' in url_parse.path) or ('ROI' in url_parse.path):
            result = "Version 7.2.0 (2020-06-19)"
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        GlobalError = wasserzaehler.CheckError()
        if GlobalError is not None:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(GlobalError, 'UTF-8'))

            return

        if "/image_tmp/" in url_parse.path:
            self.send_response(200)
            size = str(os.stat('.'+self.path).st_size)
            self.send_header('Content-type', 'image/jpg')
            self.send_header('Content-length', size)
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read()) # Read the file and send the contents
            return

        url = ''
        if 'url' in query_parse:
            url = query_parse['url'][0]

        simple = True
        if ('&full' in self.path) or ('?full' in self.path):
            simple = False

        single = False
        if ('&single' in self.path) or ('?single' in self.path):
            single = True

        usePrevalue = False
        if ('&usePreValue' in self.path) or ('?usePreValue' in self.path) or ('&usePrevalue' in self.path) or ('?usePrevalue' in self.path):
            usePrevalue = True

        value = ''
        if 'value' in query_parse:
            value = query_parse['value'][0]

        if ('crash' in url_parse.path):
            a = 1
            b = 0
            c = a / b
            return

        if ('crash' in url_parse.path):
            result = "Crash in a second"
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            print('Crash with division by zero!')
            a = 1
            b = 0
            c = a/b
            return

        if ('roi' in url_parse.path) or ('ROI' in url_parse.path):
            result = wasserzaehler.getROI(url)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        if 'setPreValue' in url_parse.path:
            result = wasserzaehler.setPreValue(value)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        if 'wasserzaehler.json' in url_parse.path:
            result = wasserzaehler.getZaehlerstandJSON(url, simple, usePrevalue, single)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

        if 'wasserzaehler' in url_parse.path:
            result = wasserzaehler.getZaehlerstand(url, simple, usePrevalue, single)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(result, 'UTF-8'))
            return

if __name__ == '__main__':

    wasserzaehler = lib.ZaehlerstandClass.Zaehlerstand()

    PORT = 3000
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        print("Wasserzaehler is serving at port", PORT)
        httpd.serve_forever()
