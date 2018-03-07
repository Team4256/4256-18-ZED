from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from io import BytesIO

import cv2

from queue import Empty

class ImageHandler(BaseHTTPRequestHandler):
    stitched_queue = None
    enabled = False
    rotation = 45

    def do_GET(self):
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            while self.enabled:
                self.rotation = (self.rotation+1)%360
                print(self.rotation)
                image = self.stitched_queue.get(True)
                while True:
                    try:
                        image = self.stitched_queue.get_nowait()
                    except Empty:
                        break


                image_jpg = cv2.imencode('.jpeg', image)[1]
                self.wfile.write("--jpgboundary".encode())
                self.send_header("Content-type", "image/jpeg")
                self.send_header("Content-length", str(image_jpg.size))
                self.end_headers()
                self.wfile.write(image_jpg.tostring())

                self.stitched_queue.task_done()#TODO can't just call here, must call after every get

        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("<html><head></head><body>".encode())
            self.wfile.write(("<img style=\"transform:rotate(" + str(self.rotation) + "deg);\" src='http://localhost:5801/cam.mjpg'/>").encode())
            self.wfile.write("</body></html>".encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class ThreadableMJPGSender(object):
    def __init__(self, stitched_queue):
        self.server = ThreadedHTTPServer(('localhost', 5801), ImageHandler)#TODO constant for ip
        ImageHandler.stitched_queue = stitched_queue

    def run(self):
        ImageHandler.enabled = True
        self.server.serve_forever()

    def stop(self):
        ImageHandler.enabled = False
        self.server.shutdown()
