from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import sys
import os
from urllib.parse import parse_qs
from typing import Callable

class CustomHTTPHandler(BaseHTTPRequestHandler):
	def serve_redirect(self):
		queryStr = ''
		if '?' in self.path:
			queryStr = self.path.split('?')[1]

		qs = parse_qs(queryStr)

		code = None
		if 'code' in qs:
			code_list = qs['code']
			if len(code_list) > 0:
				code = code_list[0]

		if code == None:
			self.send_error(422)
			return

		print("[HTTP] Received discord code: ", code, file = sys.stderr)

		if self.server.on_auth != None and self.server.on_auth(code):
			self.send_response(200)
			self.send_header('Content-Type', self.server.redirect_mime)
			self.send_header('Content-Length', self.server.redirect_size)
			self.end_headers()
			self.wfile.write(self.server.redirect_content)
		else:
			self.send_error(500)
		
		return

	def do_GET(self):
		if self.path.startswith('/discord/redirect'):
			try:
				self.serve_redirect()
			except Exception as ex:
				print("Exception: ", ex, ex.args, file = sys.stderr)
				self.send_error(500)
			finally:
				return

		
		self.send_response(200)
		self.send_header('Content-Type', self.server.index_mime)
		self.send_header('Content-Length', self.server.index_size)
		self.end_headers()
		self.wfile.write(self.server.index_content)
		return

class CustomHTTPServer(ThreadingHTTPServer):
	def __init__(self, port: int = 80, on_authentication: Callable[[str], bool] = None, redirect_target: str = 'http://localhost/discord/redirect', content_directory = './http/'):
		ThreadingHTTPServer.__init__(self, ("", port), CustomHTTPHandler)
		self.redirect_target = redirect_target
		self.on_auth = on_authentication
		self.running = False

		self.index_content = 'No content'.encode('utf-8')
		self.index_size = len(self.index_content)
		self.index_mime = 'text/plain; charset=UTF-8'

		self.redirect_content = 'Redirecting...'.encode('utf-8')
		self.redirect_size = len(self.redirect_content)
		self.redirect_mime = 'text/plain; charset=UTF-8'

		index_path = os.path.join(content_directory, 'index.html')
		redirect_path = os.path.join(content_directory, 'redirect.html')

		if os.path.exists(index_path):
			fs = open(index_path, "r")

			self.index_content = fs.read().encode('utf-8')
			self.index_size = len(self.index_content)
			self.index_mime = 'text/html; charset=UTF-8'

			fs.close()

		if os.path.exists(redirect_path):
			fs = open(redirect_path, "r")

			self.redirect_content = fs.read().encode('utf-8')
			self.redirect_size = len(self.redirect_content)
			self.redirect_mime = 'text/html; charset=UTF-8'

			fs.close()


	def start(self):
		if self.running:
			return

		self.running = True
		self.serve_forever()

	def stop(self):
		if not self.running:
			return

		self.shutdown()
		self.running = False