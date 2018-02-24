import cv2

class USB(object):
    def __init__(self, port, destination_queue):
        self.film = cv2.VideoCapture(port)
        self.destination_queue = destination_queue

    def run(self):
        while True:
            frame = self.film.read()
            if frame[0]:
                self.destination_queue.put_nowait(frame[1])

    def release(self):
        self.film.release()
