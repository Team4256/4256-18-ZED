import numpy as np
import cv2
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

class Stitching(object):
    def __init__(
        self, Lcalib_path = 'Resources/ELPFisheyeL/', Rcalib_path = 'Resources/ELPFisheyeR/',
        LR_PinchAmount = 495, Ly_Offset = 0, Ry_Offset = 10,
        Ltheta = -58, Rtheta = 60,
        queue):
        #{preparing fisheye cameras}
        self.ELPFisheyeL_calib_path = Lcalib_path
        self.ELPFisheyeR_calib_path = Rcalib_path
        self.ELPFisheyeL_calib = Undistort.load_calib(self.ELPFisheyeL_calib_path)
        self.ELPFisheyeR_calib = Undistort.load_calib(self.ELPFisheyeR_calib_path)
        #{defining other constants}
        self.LR_PinchAmount = LR_PinchAmount
        self.Ly_Offset = Ly_Offset
        self.Ry_Offset = Ry_Offset
        self.Ltheta = Ltheta
        self.Rtheta = Rtheta

        self.queue = queue


    def createCanvas():
        '''get new frame'''
        view_left = Main.left_image_queue.get()#TODO params)#self.ELPFisheyeL_film.read()
        view_right = Main.right_image_queue.get()#TODO params)#self.ELPFisheyeR_film.read()

        total_height, total_width = 0, -self.LR_PinchAmount

        if view_left[0]:# a boolean that says whether camera actually returned an image
            if not self.ELPFisheyeL_calib[0]:# a boolean that says whether calibration files exist
                #TODO Run Undistort script (...gen_calib(imgpath, savepath))
                self.ELPFisheyeL_calib = Undistort.load_calib(self.ELPFisheyeL_calib_path)
            (K, D) = self.ELPFisheyeL_calib[1]
            view_left = Undistort.simple(K, D, view_left[1])
            bird_left = Transform2D.getBirdView(view_left, Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
            final_left = Stitching.rotate(bird_left, self.Ltheta)#TODO scale parameter
            total_height = max(total_height, final_left.shape[0] + self.Ly_Offset)
            total_width += final_left.shape[1]

        if view_right[0]:# a boolean that says whether camera actually returned an image
            if not self.ELPFisheyeR_calib[0]:# a boolean that says whether calibration files exist
                #TODO Run Undistort script (...gen_calib(imgpath, savepath))
                self.ELPFisheyeR_calib = Undistort.load_calib(self.ELPFisheyeR_calib_path)
            (K, D) = self.ELPFisheyeR_calib[1]
            view_right = Undistort.simple(K, D, view_right[1])
            bird_right = Transform2D.getBirdView(view_right, Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
            final_right = Stitching.rotate(bird_right, self.Rtheta)#TODO scale parameter
            total_height = max(total_height, final_right.shape[0] + self.Ry_Offset)
            total_width += final_right.shape[1]

        if (total_width > 0):# only really need to check one to ensure both are greater than 0
            canvas = np.zeros((total_height, total_width, 3), dtype = 'uint8')
            canvas[self.Ly_Offset:self.Ly_Offset + final_left.shape[0], :final_left.shape[1]] = final_left
            canvas_right = canvas[self.Ry_Offset:self.Ry_Offset + final_right.shape[0], -final_right.shape[1]:]
            masked = canvas_right == 0
            canvas_right[masked] = final_right[masked]
            return (True, canvas)
        else:
            return (False,)


    def run():
        self.queue.put_nowait(createCanvas())
