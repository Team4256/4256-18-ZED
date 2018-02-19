#https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
#https://nikolasent.github.io/opencv/2017/05/07/Bird's-Eye-View-Transformation.html


def getBirdView(image, camera_properties):
    rows, columns = image.shape[:2]
    min_angle = 0.0
    max_angle = camera_properties.compute_max_angle()
    min_index = camera_properties.compute_min_index(rows, max_angle)
    image = image[min_index:, :]
    rows = image.shape[0]

    src_quad = camera_properties.src_quad(rows, columns)
    dst_quad = camera_properties.dst_quad(rows, columns, min_angle, max_angle)
    return perspective(image, src_quad, dst_quad)


import cv2
def perspective(image, src_quad, dst_quad):
    bottomLeft, bottomRight, topLeft, topRight = dst_quad
    # solve for the new width
    widthA = topRight[0] - topLeft[0]
    widthB = bottomRight[0] - bottomLeft[0]
    maxWidth = max(widthA, widthB)
    # solve for the new height
    heightA = bottomLeft[1] - topLeft[1]
    heightB = bottomRight[1] - topRight[1]
    maxHeight = max(heightA, heightB)

    matrix = cv2.getPerspectiveTransform(src_quad, dst_quad)
    return cv2.warpPerspective(image, matrix, (maxWidth, maxHeight))


from math import radians, cos
import numpy as np
class CameraProperties(object):
    # in an ideal world, computations would work until reaching the horizon (89.999...)
    # in the real world, the resulting distances get too big to handle
    # -- could go up to around 84.0, but to avoid lots of distortion stay a bit lower
    functional_limit = radians(77.0)
    def __init__(self, height, fov_vert, fov_horz, cameraTilt):
        '''height: the height above the ground, in any unit
        fov_vert: the vertical field of view, in degrees
        fov_horz: the horizontal field of view, in degrees
        cameraTilt: an acute angle measured from the ground, in degrees'''
        self.height = float(height)
        self.fov_vert = radians(float(fov_vert))
        self.fov_horz = radians(float(fov_horz))
        self.cameraTilt = radians(float(cameraTilt))
        self.bird_src_quad = None
        self.bird_dst_quad = None

    def src_quad(self, rows, columns):
        '''This just finds the vertices of a rectangle that covers the entire standard image'''
        if self.bird_src_quad is None:
            # bottom left, bottom right, top left, top right
            self.bird_src_quad = np.array([[0, rows - 1], [columns - 1, rows - 1], [0, 0], [columns - 1, 0]], dtype = 'float32')
        return self.bird_src_quad

    def dst_quad(self, rows, columns, min_angle, max_angle):
        '''This finds 4 points such that dragging the standard image corners onto the points results in a birds eye view'''
        if self.bird_dst_quad is None:
            # fov_offset is the angle between the bottom of the vertical FOV and the ground's normal
            fov_offset = self.cameraTilt - self.fov_vert/2.0
            # bottom_over_top represents the ratio of the base lengths of the trapezoidal image that will be formed
            bottom_over_top = cos(max_angle + fov_offset)/cos(min_angle + fov_offset)
            # dimensional analysis
            bottom_width = columns*bottom_over_top
            # since bottom is thinner than top, create black spaces to keep it centered
            blackEdge_width = (columns - bottom_width)/2
            leftX = blackEdge_width
            rightX = leftX + bottom_width
            # bottom left, bottom right, top left, top right
            self.bird_dst_quad = np.array([[leftX, rows], [rightX, rows], [0, 0], [columns, 0]], dtype = 'float32')
        return self.bird_dst_quad

    def reset(self):
        self.bird_src_quad = None
        self.bird_dst_quad = None

    def compute_min_index(self, rows, max_angle):
        return int(rows*(1.0 - max_angle/self.fov_vert))

    def compute_max_angle(self):
        return min(CameraProperties.functional_limit - self.cameraTilt + self.fov_vert/2.0, self.fov_vert)


ELPFisheye = CameraProperties(40.0, 170.0, 170.0, 54.7)#TODO get accurate first parameter, which is height
ZED = CameraProperties(20.0, 54.0, 96.0, 90.0)#TODO get accurate first parameter, which is height
