import SimpleHTTPServer
import SocketServer


class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
  def do_GET(self):
      # Your code here
      print "Client requested:", self.command, self.path

      DUMMY_RESPONSE = 'error 404'
      self.send_response(404)
      self.send_header("Content-length", len(DUMMY_RESPONSE))
      self.end_headers()
      self.wfile.write(DUMMY_RESPONSE)

  def do_HEAD(self):
      # Your code here
      print "Client requested:", self.command, self.path

      DUMMY_RESPONSE = 'error 404'
      self.send_response(404)
      self.send_header("Content-length", len(DUMMY_RESPONSE))
      self.end_headers()
      self.wfile.write(DUMMY_RESPONSE)

PORT = 8000

httpd = SocketServer.TCPServer(("", PORT), MyHandler)

print "Serving at port:", PORT
httpd.serve_forever()
   
