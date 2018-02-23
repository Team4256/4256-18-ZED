#{BUILT-INS}
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer
# from SocketServer import ThreadingMixIn
from socketserver import ThreadingMixIn
# import StringIO
from io import StringIO, BytesIO
import threading
import time
#{3RD PARTY}
import cv2
from PIL import Image as convertToJPG

class ImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        import Main
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            while True:
                try:
                    ret, image = Main.camera.read()
                    if not ret:
                        continue
                    image_rgb = cv2.cvtColor(cv2.pyrDown(image), cv2.COLOR_BGR2RGB)
                    image_jpg = convertToJPG.fromarray(image_rgb)
                    tempFile = BytesIO()
                    image_jpg.save(tempFile, "JPEG")
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Content-length", str(tempFile.getbuffer().nbytes))
                    self.end_headers()
                    self.wfile.write(tempFile.getvalue())
                    #image_jpg.save(self.wfile, "JPEG")
                    time.sleep(0.05)
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><head></head><body>".encode())
            self.wfile.write("<img src='http://127.0.0.1:8080/cam.mjpg'/>".encode())
            self.wfile.write("</body></html>".encode())
            return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
