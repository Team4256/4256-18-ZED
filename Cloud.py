"""https://github.com/VincentCheungM/lidar_projection/blob/master/show.py"""
import numpy as np

def scale_to_255(array, minimum, maximum):
    return (255*(array - minimum)/float(maximum - minimum)).astype(array.dtype)

def birds_eye_projection(cloud, x_range = (-10, 10), y_range = (-10, 10), z_range = (-3, 3), res = 1):
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

cloud = np.load("cloud.npy")
print(birds_eye_projection(cloud))
