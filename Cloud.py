def scale_to_255(array, minimum, maximum):
    return (255*(array - minimum)/float(maximum - minimum)).astype(array.dtype)

from math import acos
from math import radians as to_rads
def lowest_angle_for(depth, camera_properties, radians = False):# depth and height must be in same units
    '''Imagine that the camera lies at the center of a circle with radius depth.
    That circle intersects the ground at some point, P. This function returns the
    angle between the lower boundary of the camera's vertical_fov and point P.'''
    big_angle = acos(camera_properties.height/float(depth))
    lowest_angle = to_degrees(big_angle) - camera_properties.get_lens_to_ground_angle() + camera_properties.get_vertical_fov()/2.0
    return to_rads(lowest_angle) if radians else lowest_angle


from math import radians as to_rads
class CameraProperties(object):
    def __init__(self, height, lens_to_ground_angle = 90.0, vertical_fov = 70.0):
        self.height = float(height)
        self.lens_to_ground_angle = float(lens_to_ground_angle)
        self.vertical_fov = float(vertical_fov)
    def get_lens_to_ground_angle(self, radians = False):
        return to_rads(self.lens_to_ground_angle) if radians else self.lens_to_ground_angle
    def get_vertical_fov(self, radians = False):
        return to_rads(self.vertical_fov) if radians else self.vertical_fov

import numpy as np
from math import ceil
class DepthMap(object):
    def __init__(self, depth_map):
        self.depth_map = depth_map
        self.height, self.width = depth_map.shape[:2]
        self.min, self.max = depth_map.min(), depth_map.max()
    def bird_view(resolution = 10):
        section_size = (self.max - self.min)/float(resolution)# don't use .ptp(), already have .max and .min
        sections = np.zeros((self.height, self.width, resolution), dtype = 'uint32')
        for i in range(resolution):
            indices = np.logical_and((self.depth_map >= i*section_size), (self.depth_map < (i+1)*section_size))
            sections[indices, i] = 1
        return sections.sum(axis = 0).transpose()
    def bird_view_y_aware(resolution = 10, camera_properties):
        section_size = (self.max - self.min)/float(resolution)# could use .ptp() instead of .max() - .min()
        sections = np.zeros((self.height, self.width, resolution), dtype = 'uint32')
        for i in range(resolution):
            indices = np.logical_and((depth_map >= i*section_size), (depth_map < (i+1)*section_size))
            sections[indices, i] = 1
            # avg_depth = self.depth_map[indices].mean()# don't do this for time's sake
            avg_depth = (i+.5)*section_size
            minimum_height = self.height*(lowest_angle_for(avg_depth, camera_properties)/camera_properties.get_vertical_fov())# basically (max height)*(% of the way up)
            minimum_height = ceil(minimum_height)
            y_mult_A = np.zeros((minimum_height), dtype = 'uint8')
            y_mult_B = np.arange(minimum_height, self.height, dtype = 'uint8')
            y_mult = np.concatenate(y_mult_A, y_mult_B)
            sections[:,:,i] *= y_mult[:, None]
        return sections.mean(axis = 0).transpose()#TODO mean will count all the 0's, resulting in dimmer result



def get_top_from_front(depth_map, section_count = 10):
    section_size = depth_map.ptp()/section_count# max - min
    rows, columns = depth_map.shape[:2]
    sections = np.zeros((rows, columns, section_count), dtype = 'uint32')
    for i in range(section_count):
        indices = np.logical_and((depth_map >= i*section_size), (depth_map < (i+1)*section_size))
        sections[indices, i] = 1
    y_mult = np.arange(0, rows, dtype = 'uint32')[:, None, None]
    sections *= y_mult
    return sections.mean(axis = 0).transpose()


if __name__ == '__main__':
    '''This is meant to be used for debugging purposes; works with any depth map image.'''
    import cv2
    import time
    #{Prepare depth map from file}
    depth_map = np.load('sample depth map.npy')# get grayscale depth map
    depth_map[~np.isfinite(depth_map)] = 0# remove bad values like inf
    depth_map = cv2.pyrDown(depth_map)# shrink to speed up computations
    depth_map = depth_map.max() - depth_map
    #{Do the conversion}
    start_time = time.time()
    top_view = get_top_from_front(depth_map)
    conversion_time = time.time() - start_time
    print('The conversion took {} seconds'.format(conversion_time))
    #{Prepare vars for resizing}
    result_width = depth_map.shape[1]
    result_height = 200
    hsv = np.full((result_height, result_width, 3), 255, dtype = 'uint8')# prepare empty array for colored result
    #{Display}
    top_view *= 255/top_view.max()# scales to make new max() 255
    result = cv2.resize(top_view.astype('uint8'), (result_width, result_height), interpolation = cv2.INTER_LINEAR)# stretch the height
    hsv[:,:,0] = result
    cv2.imshow('Depth Map', (depth_map*255/depth_map.max()).astype('uint8'))
    cv2.imshow('Top View', cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    cv2.waitKey(0)
