import cv2

class ThreadableGrabber(object):
    def __init__(self, port, destination_queue):
        self.destination_queue = destination_queue
        self.film = cv2.VideoCapture(port)
        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            frame = self.film.read()
            if frame[0]:
                self.destination_queue.put(frame[1])

        self._release()

    def _release(self):
        self.film.release()

    def stop(self):
        self.enabled = False
