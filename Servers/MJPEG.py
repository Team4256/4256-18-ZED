#{BUILT-INS}
# from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, HTTPServer
# from SocketServer import ThreadingMixIn
from socketserver import ThreadingMixIn
# import StringIO
from io import StringIO, BytesIO
import threading
from queue import Queue
import time
#{3RD PARTY}
import cv2
from PIL import Image as convertToJPG
from queue import Empty

class ImageHandler(BaseHTTPRequestHandler):
    stitching_queue = None

    def do_GET(self):
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            while True:
                try:
                    if self.stitching_queue.empty():
                        image = self.stitching_queue.get(True)
                    else:
                        while True:
                            try:
                                image = self.stitching_queue.get_nowait()
                            except Empty:
                                break


                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image_jpg = convertToJPG.fromarray(image_rgb)
                    tempFile = BytesIO()
                    image_jpg.save(tempFile, "JPEG")
                    self.wfile.write("--jpgboundary".encode())
                    self.send_header("Content-type", "image/jpeg")
                    self.send_header("Content-length", str(tempFile.getbuffer().nbytes))
                    self.end_headers()
                    self.wfile.write(tempFile.getvalue())

                    self.stitching_queue.task_done()#TODO use this everywhere
                except KeyboardInterrupt:#TODO doesn't end right
                    print('done')
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
