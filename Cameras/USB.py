import cv2
import numpy as np
from Transform import Undistort

def highlight_cubes(image):
    image = np.rot90(image, 2)
    return cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)[:,:,2]

class USB(object):
    def __init__(self, port, calibration_path):
        self.film = cv2.VideoCapture(port)
        self.film.set(3, 1920//4)
        self.film.set(4, 1080//4)
        self.K, self.D = Undistort.load_calib(calibration_path, image_size_ratio = 0.25)

        self.enabled = False

    def get(self):
        self.enabled = True

        frame = self.film.read()
        if frame[0]:
            highlighted = highlight_cubes(frame[1])
            undistorted = Undistort.simple(self.K, self.D, highlighted)# THIS IS THE SLOWEST PART OF THE CODE
            return (True, undistorted)
        else:
            return (False,)


    def _release(self):
        self.film.release()
