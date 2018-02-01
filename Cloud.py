'''https://github.com/VincentCheungM/lidar_projection/blob/master/show.py'''
import numpy as np

def scale_to_255(array, minimum, maximum):
    return (255*(array - minimum)/float(maximum - minimum)).astype(array.dtype)

def birds_eye_projection(cloud, x_range = (-100, 100), y_range = (-100, 100), z_range = (-100, 100), res = 1.0):
    rows, columns = cloud.shape[:2]
    cloud = cloud.reshape((rows*columns, -1))#.astype('int32')
    cloudX, cloudY, cloudZ, color = np.split(cloud, 4, axis = 1)# 4 to get color too

    ff = np.logical_and((cloudY > y_range[0]), (cloudY < y_range[1]))
    ss = np.logical_and((cloudX > x_range[0]), (cloudX < x_range[1]))

    indices = np.argwhere(np.logical_and(ff, ss)).flatten()

    imgX = (cloudX[indices]/res)#.astype('int32')
    imgY = (cloudY[indices]/res)#.astype('int32')

    imgX = imgX[np.isfinite(imgX)]# remove nan and infinities
    imgY = imgY[np.isfinite(imgY)]
    #x = x[numpy.logical_not(numpy.isnan(x))]
    #x = x[~numpy.isnan(x)]

    imgX -= int(np.floor(x_range[0]/res))
    imgY -= int(np.floor(y_range[0]/res))

    validZ = cloudZ[indices]
    validZ = validZ[np.isfinite(validZ)]

    pixel_values = np.clip(validZ, z_range[0], z_range[1])
    pixel_values = scale_to_255(pixel_values, z_range[0], z_range[1])

    x_max = int((x_range[1] - x_range[0])/res)
    y_max = int((y_range[1] - y_range[0])/res)

    img = np.zeros((y_max, x_max), dtype = 'uint8')

    img[-imgY.astype('int32'), imgX.astype('int32')] = pixel_values
    return img



def get_top_from_front(depth_map, section_count = 127):
    section_size = depth_map.ptp()/section_count# max - min
    rows, columns = depth_map.shape[:2]
    sections = np.zeros((rows, columns, section_count), dtype = 'uint32')
    for i in range(section_count):
        indices = np.logical_and((depth_map >= i*section_size), (depth_map < (i+1)*section_size))
        sections[indices, i] = 1#depth_map[indices]
    y_mult = np.arange(0, rows, dtype = 'uint32')[:, None, None]
    sections *= y_mult
    return sections.mean(axis = 0).transpose()


if __name__ == '__main__':
    '''This is meant to be used for debugging purposes; works with any depth map image.'''
    import cv2
    depth_map = cv2.imread('depth.jpg', 0)# get grayscale depth map
    result_width = depth_map.shape[1]
    result_height = 200
    hsv = np.full((result_height, result_width, 3), 255, dtype = 'uint8')# prepare empty array for colored result
    top_view = get_top_from_front(depth_map)
    top_view *= 255/top_view.max()# scales to make new max() 255
    result = cv2.resize(top_view.astype('uint8'), (result_width, result_height), interpolation = cv2.INTER_LINEAR)# stretch the height
    hsv[:,:,0] = result
    cv2.imshow('Depth Map', depth_map)
    cv2.imshow('Top View', cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))
    cv2.waitKey(0)
