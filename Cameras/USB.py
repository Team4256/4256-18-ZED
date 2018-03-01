import cv2
import numpy as np
import Undistort
import Transform2D

def highlight_cubes(image):
    # image = cv2.pyrDown(cv2.pyrDown(image))# taken care of by film.set()
    image = np.rot90(image, 2)
    v = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:,:,2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype('float32')
    gray[v > 200] = 255
    gray[v <= 200] *= 0.5
    return gray.astype('uint8')

class ThreadableGrabber(object):
    def __init__(self, port, destination_queue, calibration_path):
        self.destination_queue = destination_queue
        self.film = cv2.VideoCapture(port)
        self.film.set(3, 1920//4)
        self.film.set(4, 1080//4)
        self.K, self.D = Undistort.load_calib(calibration_path, image_size_ratio = 0.25)

        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            frame = self.film.read()
            if frame[0]:
                highlighted = highlight_cubes(frame)
                undistorted = Undistort.simple(self.K, self.D, highlighted)# THIS IS THE SLOWEST PART OF THE CODE
                self.destination_queue.put(undistorted)

        self._release()

    def _release(self):
        self.film.release()

    def stop(self):
        self.enabled = False
