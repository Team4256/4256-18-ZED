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
        LR_PinchAmount = 800//4, Ly_Offset = 112//4, Ry_Offset = 0,
        Ltheta = -60, Rtheta = 56):
        #{defining other constants}
        self.LR_PinchAmount = LR_PinchAmount
        self.Ly_Offset = Ly_Offset
        self.Ry_Offset = Ry_Offset
        self.Ltheta = Ltheta
        self.Rtheta = Rtheta
        self.LScaleFactor = .95

        self.Lqueue = Lqueue
        self.Rqueue = Rqueue
        self.ZEDqueue = ZEDqueue
        self.destination_queue = destination_queue

        self.ready = False

        self.enabled = False

    def get_ready(self, view_left, view_right, view_zed):
        bird_left = Transform2D.getBirdView(view_left[1], Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
        final_left = rotate(bird_left, self.Ltheta, self.LScaleFactor)

        bird_right = Transform2D.getBirdView(view_right[1], Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
        final_right = rotate(bird_right, self.Rtheta)

        self.total_height = max(final_left.shape[0] + self.Ly_Offset, final_right.shape[0] + self.Ry_Offset)
        self.total_width = final_left.shape[1] + final_right.shape[1] - self.LR_PinchAmount

        self.canvas = np.zeros((self.total_height, self.total_width), dtype = 'uint16')
        self.ready = True

    def createCanvas(self, view_left, view_right, view_zed):
        '''get new frame'''
        if view_left[0] and view_right[0]:
            bird_left = Transform2D.getBirdView(view_left[1], Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
            final_left = rotate(bird_left, self.Ltheta, self.LScaleFactor)

            bird_right = Transform2D.getBirdView(view_right[1], Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
            final_right = rotate(bird_right, self.Rtheta)

            canvas_left = self.canvas[self.Ly_Offset:self.Ly_Offset + final_left.shape[0], :final_left.shape[1]]
            canvas_right = self.canvas[self.Ry_Offset:self.Ry_Offset + final_right.shape[0], -final_right.shape[1]:]

            canvas_left = final_left
            zero_map = canvas_right == 0
            canvas_right[zero_map] = final_right[zero_map]
        elif view_left[0]:
            bird_left = Transform2D.getBirdView(view_left[1], Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
            final_left = rotate(bird_left, self.Ltheta, self.LScaleFactor)
            canvas_left = self.canvas[self.Ly_Offset:self.Ly_Offset + final_left.shape[0], :final_left.shape[1]]

            useful_map = final_left > 0
            canvas_left[useful_map] = final_left[useful_map]
        elif view_right[0]:
            bird_right = Transform2D.getBirdView(view_right[1], Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
            final_right = rotate(bird_right, self.Rtheta)
            canvas_right = self.canvas[self.Ry_Offset:self.Ry_Offset + final_right.shape[0], -final_right.shape[1]:]

            useful_map = final_right > 0
            canvas_right[useful_map] = final_right[useful_map]

        return self.canvas.astype('uint8')


    def run(self):
        self.enabled = True
        #TODO timeout period if cameras arent responding
        view_left = (True, self.Lqueue.get(True))
        view_right = (True, self.Rqueue.get(True))
        view_zed = (False,)#(True, self.ZEDqueue.get(True))
        self.get_ready(view_left, view_right, view_zed)

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
