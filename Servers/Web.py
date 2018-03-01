from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from io import BytesIO

import cv2
from PIL import Image as convertToJPG

from queue import Empty

class ImageHandler(BaseHTTPRequestHandler):
    stitched_queue = None
    enabled = False

    def do_GET(self):
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            while self.enabled:
                if self.stitched_queue.empty():
                    image = self.stitched_queue.get(True)
                else:
                    while True:
                        try:
                            image = self.stitched_queue.get_nowait()
                        except Empty:
                            break


                image_jpg = convertToJPG.fromarray(image)
                tempFile = BytesIO()
                image_jpg.save(tempFile, "JPEG")
                self.wfile.write("--jpgboundary".encode())
                self.send_header("Content-type", "image/jpeg")
                self.send_header("Content-length", str(tempFile.getbuffer().nbytes))
                self.end_headers()
                self.wfile.write(tempFile.getvalue())

                self.stitched_queue.task_done()#TODO can't just call here, must call after every get

        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><head></head><body>".encode())
            self.wfile.write("<img src='http://10.42.56.112:5801/cam.mjpg'/>".encode())
            self.wfile.write("</body></html>".encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class ThreadableMJPGSender(object):
    def __init__(self, stitched_queue):
        self.server = ThreadedHTTPServer(('10.42.56.112', 5801), ImageHandler)#TODO constant for ip
        ImageHandler.stitched_queue = stitched_queue

    def run(self):
        ImageHandler.enabled = True
        self.server.serve_forever()

    def stop(self):
        ImageHandler.enabled = False
        self.server.shutdown()
