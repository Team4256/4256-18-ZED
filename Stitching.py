import numpy as np
import cv2
import Transform2D
from math import radians, sin, cos, floor, ceil
from scipy.ndimage.interpolation import rotate

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
    # rotated_rect_height = abs(bird_width*sin(theta_radians)) + abs(bird_height*cos(theta_radians))
    # rotated_rect_width = abs(bird_width*cos(theta_radians)) + abs(bird_height*sin(theta_radians))
    #
    # frame_height = abs(rotated_rect_width*sin(theta_radians)) + abs(rotated_rect_height*cos(theta_radians))
    # frame_width = abs(rotated_rect_width*cos(theta_radians)) + abs(rotated_rect_height*sin(theta_radians))
    #
    # rotation_frame = np.zeros((ceil(frame_height), ceil(frame_width), 3), dtype = 'uint8')
    # row_placement = floor((frame_height - bird_height)/2.0)
    # col_placement = floor((frame_width - bird_width)/2.0)
    # rotation_frame[row_placement:row_placement + bird_height, col_placement:col_placement + bird_width] = bird
    #
    # rot_matrix = cv2.getRotationMatrix2D((frame_width/2, frame_height/2), theta, 1)
    #
    # dst = cv2.warpAffine(rotation_frame, rot_matrix, (int(frame_width), int(frame_height)))
    #
    # row_placement = floor((frame_height - rotated_rect_height)/2.0)
    # col_placement = floor((frame_width - rotated_rect_width)/2.0)
    # rotated_rect = dst[row_placement:-row_placement, col_placement:-col_placement]

camera_port = 2

# film = cv2.VideoCapture(camera_port)

while True:#film.isOpened():
    # view_left = film.read()[1]
    view_right = cv2.pyrDown(cv2.imread("Test A.jpg"))
    view_left = cv2.pyrDown(cv2.imread("Test B.jpg"))
    view_aft = cv2.imread("Test C.jpg")

    bird_right = Transform2D.getBirdView(view_right, Transform2D.ELPFisheye)
    bird_left = Transform2D.getBirdView(view_left, Transform2D.ELPFisheye)
    bird_aft = Transform2D.getBirdView(view_aft, Transform2D.ZED)
    # bird = np.rot90(bird, 3)
    # bird_height, bird_width = bird.shape[:2]

    theta = 60
    rotated_right = rotate(bird_right, theta)
    rotated_left = rotate(bird_left, -theta)
    rotated_aft = rotate(bird_aft, 180)

    pinchAmount = 400;

    total_height = rotated_right.shape[0]
    total_width = rotated_right.shape[1] + rotated_left.shape[1] - pinchAmount
    canvas = np.zeros((total_height, total_width, 3), dtype = 'uint8')
    canvas[:,:rotated_left.shape[1]] = rotated_left
    canvas_right = canvas[:,-rotated_right.shape[1]:]
    canvas_right[canvas_right == 0] = rotated_right[canvas_right == 0]


    cv2.imshow("Canvas", canvas)
    cv2.imshow("Aft", rotated_aft)

    ch = 0xFF & cv2.waitKey(1)
    if ch == 27:
        break

cv2.destroyAllWindows()
# film.release()
