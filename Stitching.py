import numpy as np
import cv2
import Transform2D
import Undistort
from queue import Empty

def rotate(image, angle, scale = 1.0):
    #https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
    height, width = image.shape[:2]
    cX, cY = (width//2, height//2)

    matrix = cv2.getRotationMatrix2D((cX, cY), -angle, scale)
    matrix_cos = np.abs(matrix[0, 0])
    matrix_sin = np.abs(matrix[0, 1])

    height_rotated = int((height*matrix_cos) + (width*matrix_sin))
    width_rotated = int((height*matrix_sin) + (width*matrix_cos))

    matrix[0, 2] += (width_rotated/2) - cX
    matrix[1, 2] += (height_rotated/2) - cY
    return cv2.warpAffine(image, matrix, (width_rotated, height_rotated))


class ThreadableStitcher(object):
    def __init__(
        self, Lqueue, Rqueue, ZEDqueue, destination_queue,
        LR_PinchAmount = 430, Ly_Offset = 0, Ry_Offset = 0,
        Ltheta = -62, Rtheta = 59):
        #{defining other constants}
        self.LR_PinchAmount = LR_PinchAmount
        self.Ly_Offset = Ly_Offset
        self.Ry_Offset = Ry_Offset
        self.Ltheta = Ltheta
        self.Rtheta = Rtheta

        self.Lqueue = Lqueue
        self.Rqueue = Rqueue
        self.ZEDqueue = ZEDqueue
        self.destination_queue = destination_queue

        self.canvas = None

        self.enabled = False


    def createCanvas(self, view_left, view_right, view_zed):
        '''get new frame'''
        total_height, total_width = 0, -self.LR_PinchAmount
        import time

        if view_left[0]:
            bird_left = Transform2D.getBirdView(view_left[1], Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
            final_left = rotate(bird_left, self.Ltheta)#TODO scale parameter
            total_height = max(total_height, final_left.shape[0] + self.Ly_Offset)
            total_width += final_left.shape[1]

            ##############
            if self.canvas is not None:
                self.canvas[self.Ly_Offset:self.Ly_Offset + final_left.shape[0], :final_left.shape[1]] = final_left

        if view_right[0]:
            bird_right = Transform2D.getBirdView(view_right[1], Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
            final_right = rotate(bird_right, self.Rtheta)#TODO scale parameter
            total_height = max(total_height, final_right.shape[0] + self.Ry_Offset)
            total_width += final_right.shape[1]

            ##############
            if self.canvas is not None:
                self.canvas[self.Ry_Offset:self.Ry_Offset + final_right.shape[0], -final_right.shape[1]:] = final_right

        if self.canvas is None:
            self.canvas = np.zeros((total_height, total_width), dtype = 'uint8')

        return self.canvas


    def run(self):
        self.enabled = True
        #TODO timeout period if cameras arent responding
        view_left = (True, self.Lqueue.get(True))
        view_right = (True, self.Rqueue.get(True))
        view_zed = (False,)#(True, self.ZEDqueue.get(True))
        self.destination_queue.put(self.createCanvas(view_left, view_right, view_zed))

        while self.enabled:
            view_left = (False,)
            view_right = (False,)
            view_zed = (False,)
            while True:
                try:
                    view_left = (True, self.Lqueue.get_nowait())# TODO need to run task_done every time we get
                except Empty:
                    break
            while True:
                try:
                    view_right = (True, self.Rqueue.get_nowait())# TODO need to run task_done every time we get
                except Empty:
                    break
            while True:
                try:
                    view_zed = (True, self.ZEDqueue.get_nowait())# TODO need to run task_done every time we get
                except Empty:
                    break


            if view_left[0] or view_right[0] or view_zed[0]:
                self.destination_queue.put(self.createCanvas(view_left, view_right, view_zed))

    def stop(self):
        self.enabled = False
