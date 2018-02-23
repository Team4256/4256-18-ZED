#{3RD PARTY}
import cv2
#{CUSTOM}
from ServerMJPEG import ImageHandler, ThreadedHTTPServer

camera = cv2.VideoCapture(0)

def streamFromCamera():
    try:
        server = ThreadedHTTPServer(('localhost', 8080), ImageHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        camera.release()
        server.socket.close()

if __name__ == '__main__':
    streamFromCamera()
