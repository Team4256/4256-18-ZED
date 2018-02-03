import numpy as np
import cv2
from Transform import TwoD

from CustomThread import Threadable
class ThreadableStitcher(Threadable):
    def __init__(
        self, cameraL, cameraR, destination_queue,
        overlapAmount = 0, upperBorderL = 0, upperBorderR = 0, thetaL = 0, thetaR = 0):

        self.cameraL = cameraL
        self.cameraR = cameraR
        self.destination_queue = destination_queue

        self.overlapAmount = overlapAmount
        self.upperBorderL = upperBorderL
        self.upperBorderR = upperBorderR
        self.thetaL = thetaL
        self.thetaR = thetaR

        self.ready = False
        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            view_left = (False,)
            view_right = (False,)
            while not view_left[0]:
                view_left = self.cameraL.get()
            while not view_right[0]:
                view_right = self.cameraR.get()

            if not self.ready:
                self.get_ready(view_left[1], view_right[1], None)
            else:
                self.create_canvas(view_left[1], view_right[1], None)

            #{following code should probably be in its own thread}
            thresholded = np.zeros_like(view_left[1])
            thresholded[view_left[1] <= 50] = 255#TODO tune
            _, contours, _ = cv2.findContours(thresholded, mode = cv2.RETR_LIST, method = cv2.CHAIN_APPROX_SIMPLE)
            targetL = thresholded.shape[1]
            targetR = 0.0
            for contour in contours:
                center, size, angle = cv2.minAreaRect(contour)
                if size[0]*size[1] > 5 and round(size[0]/size[1], 0) == 1:#TODO tune
                    if targetL > center[0]: targetL = center[0]
                    if targetR < center[0]: targetR = center[0]
            print(targetL)
            #---------------------------------------
            self.destination_queue.put(self.canvas)


    def stop(self):
        self.enabled = False

    def get_ready(self, view_left, view_right, view_zed):
        # bird_left = TwoD.getBirdView(view_left, TwoD.ELPFisheyeL)
        final_left = view_left#TwoD.rotate(bird_left, self.thetaL)

        # bird_right = TwoD.getBirdView(view_right, TwoD.ELPFisheyeR)
        final_right = view_right#TwoD.rotate(bird_right, self.thetaR)

        self.total_height = max(final_left.shape[0] + self.upperBorderL, final_right.shape[0] + self.upperBorderR)
        self.total_width = final_left.shape[1] + final_right.shape[1] - self.overlapAmount

        self.canvas = np.zeros((self.total_height, self.total_width), dtype = 'uint8')
        self.ready = True

    def create_canvas(self, view_left, view_right, view_zed):
        '''get new frame'''
        # bird_left = TwoD.getBirdView(view_left, TwoD.ELPFisheyeL)
        final_left = view_left#TwoD.rotate(bird_left, self.thetaL)

        # bird_right = TwoD.getBirdView(view_right, TwoD.ELPFisheyeR)
        final_right = view_right#TwoD.rotate(bird_right, self.thetaR)

        self.canvas[self.upperBorderL:self.upperBorderL + final_left.shape[0], :final_left.shape[1]] = final_left
        nonzero_map = final_right != 0
        self.canvas[self.upperBorderR:self.upperBorderR + final_right.shape[0], -final_right.shape[1]:][nonzero_map] = final_right[nonzero_map]
