import numpy as np
import cv2
import Transform2D
import Undistort

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
        self, cameraL, cameraR, destination_queue,
        LR_PinchAmount = 600//4, Ly_Offset = 48//4, Ry_Offset = 0//4,
        Ltheta = -60, Rtheta = 56):
        #{defining other constants}
        self.LR_PinchAmount = LR_PinchAmount
        self.Ly_Offset = Ly_Offset
        self.Ry_Offset = Ry_Offset
        self.Ltheta = Ltheta
        self.Rtheta = Rtheta
        self.LScaleFactor = 1.0

        self.cameraL = cameraL
        self.cameraR = cameraR
        self.destination_queue = destination_queue

        self.ready = False

        self.enabled = False

    def get_ready(self, view_left, view_right, view_zed):
        bird_left = Transform2D.getBirdView(view_left, Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
        final_left = rotate(bird_left, self.Ltheta, self.LScaleFactor)

        bird_right = Transform2D.getBirdView(view_right, Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
        final_right = rotate(bird_right, self.Rtheta)

        self.total_height = max(final_left.shape[0] + self.Ly_Offset, final_right.shape[0] + self.Ry_Offset)
        self.total_width = final_left.shape[1] + final_right.shape[1] - self.LR_PinchAmount

        self.canvas = np.zeros((self.total_height, self.total_width), dtype = 'uint8')
        self.ready = True

    def create_canvas(self, view_left, view_right, view_zed):
        '''get new frame'''
        bird_left = Transform2D.getBirdView(view_left, Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
        final_left = rotate(bird_left, self.Ltheta, self.LScaleFactor)

        bird_right = Transform2D.getBirdView(view_right, Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
        final_right = rotate(bird_right, self.Rtheta)

        self.canvas[self.Ly_Offset:self.Ly_Offset + final_left.shape[0], :final_left.shape[1]] = final_left
        nonzero_map = final_right != 0
        self.canvas[self.Ry_Offset:self.Ry_Offset + final_right.shape[0], -final_right.shape[1]:][nonzero_map] = final_right[nonzero_map]


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

            self.destination_queue.put(cv2.pyrDown(self.canvas))


    def stop(self):
        self.enabled = False
