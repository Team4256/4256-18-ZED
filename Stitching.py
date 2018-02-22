import numpy as np
import cv2

def rotate(image, angle, scale = 1.0):
    #TODO doc that its from pyimage search rotate bound
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


if __name__ == '__main__':
    '''This is meant to be used for debugging purposes; works with any 3 color images.'''
    import Transform2D
    import Undistort

    K = np.load('K.npy')/2.0
    K[2][2] = 1.0
    D = np.load('D.npy')/2.0

    view_left = cv2.pyrDown(cv2.imread('Test A.jpg'))
    view_right = cv2.pyrDown(cv2.imread('Test B.jpg'))
    view_aft = cv2.imread('Test C.jpg')

    view_left = Undistort.simple(K, D, view_left)
    view_right = Undistort.simple(K, D, view_right)

    bird_left = Transform2D.getBirdView(view_left, Transform2D.ELPFisheyeL)
    bird_right = Transform2D.getBirdView(view_right, Transform2D.ELPFisheyeR)
    bird_aft = Transform2D.getBirdView(view_aft, Transform2D.ZED)

    thetaL = 58
    thetaR = 60
    rotated_left = rotate(bird_left, -thetaL)
    rotated_right = rotate(bird_right, thetaR)
    rotated_aft = rotate(bird_aft, 180)

    pinchAmount = 495
    leftY = 0
    rightY = 10

    total_height = rotated_right.shape[0] + max(leftY, rightY)
    total_width = rotated_right.shape[1] + rotated_left.shape[1] - pinchAmount

    canvas = np.zeros((total_height, total_width, 3), dtype = 'uint8')
    canvas[leftY:leftY + rotated_left.shape[0], :rotated_left.shape[1]] = rotated_left
    canvas_right = canvas[rightY:rightY + rotated_right.shape[0], -rotated_right.shape[1]:]
    canvas_right[canvas_right == 0] = rotated_right[canvas_right == 0]


    cv2.imshow("Canvas", canvas)
    cv2.imshow("Aft", rotated_aft)
    cv2.waitKey(0)
