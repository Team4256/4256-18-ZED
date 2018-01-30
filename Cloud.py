"""https://github.com/VincentCheungM/lidar_projection/blob/master/show.py"""
import numpy as np

def scale_to_255(array, minimum, maximum):
    return (255*(array - minimum)/float(maximum - minimum)).astype(array.dtype)

def birds_eye_projection(cloud, x_range = (-10, 10), y_range = (-10, 10), z_range = (-3, 3), res = 0.1):
    rows, columns = cloud.shape[:2]
    cloud = cloud.reshape((rows*columns, -1))
    cloudX, cloudY, cloudZ, color = np.split(cloud, 4, axis = 1)# 4 to get color too

    ff = np.logical_and((cloudY > y_range[0]), (cloudY < y_range[1]))
    ss = np.logical_and((cloudX > x_range[0]), (cloudX < x_range[1]))
    #TODO does simple [x > bla] and [x < bla2] work?

    indices = np.argwhere(np.logical_and(ff, ss)).flatten()

    imgX = (cloudX[indices]/res).astype(np.int32)
    imgY = (cloudY[indices]/res).astype(np.int32)

    imgX -= int(np.floor(x_range[0]/res))
    imgY -= int(np.floor(y_range[0]/res))

    pixel_values = np.clip(cloudZ[indices], z_range[0], z_range[1])
    pixel_values = scale_to_255(pixel_values, z_range[0], z_range[1])

    x_max = int((x_range[1] - x_range[0])/res)
    y_max = int((y_range[1] - y_range[0])/res)

    img = np.zeros((y_max, x_max), dtype = 'uint8')
    img[-imgY, imgX] = pixel_values
    return img

cloud = np.load("cloud.npy")
print(birds_eye_projection(cloud))
