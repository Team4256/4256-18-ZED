from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from io import BytesIO
from time import sleep

import cv2

from queue import Empty

class ImageHandler(BaseHTTPRequestHandler):
    stitched_queue = None
    robot_data = None

    enabled = False

    def do_GET(self):
        if self.path.endswith(".mjpg"):
            self.send_response(200)
            self.send_header("Content-type", "multipart/x-mixed-replace; boundary=--jpgboundary")
            self.end_headers()
            while self.enabled:
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


        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("""
                <html>
                  <head>
                  </head>
                  <body>
                    <img src="/canvas.mjpg" style="position: absolute;margin-left: 25%;top: 25%;" name="image"/>
                    <script type="text/javascript">

                    var updateSource = new EventSource("/updates.gyro");

                    updateSource.onmessage = function(event) {image.style.transform = "rotate(" + event.data.toString() + "deg)";};

                    </script>
                  </body>
                </html>
                """.encode())


        if self.path.endswith('.gyro'):
            self.send_response(200)
            self.send_header("Content-type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            while self.enabled:
                gyro_angle = self.robot_data.getNumber('Gyro', 0.0)
                self.wfile.write("data: {}\n\n".format(gyro_angle).encode())
                sleep(0.6)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


from CustomThread import Threadable
class ThreadableMJPGSender(Threadable):
    def __init__(self, stitched_queue, robot_data):
        self.server = ThreadedHTTPServer(('10.42.56.11', 5803), ImageHandler)
        ImageHandler.stitched_queue = stitched_queue
        ImageHandler.robot_data = robot_data

    def run(self):
        ImageHandler.enabled = True
        self.server.serve_forever()

    def stop(self):
        ImageHandler.enabled = False
        self.server.shutdown()
