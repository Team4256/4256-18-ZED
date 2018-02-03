#https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0
#https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-part-2-13990f1b157f

import cv2
import numpy as np

def simple(K, D, image):
    '''This function undistorts the image and cuts off the parts that would look weird.'''
    rows, columns = image.shape[:2]

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (columns, rows), cv2.CV_16SC2)
    return cv2.remap(image, map1, map2, interpolation = cv2.INTER_LINEAR, borderMode = cv2.BORDER_CONSTANT)


def advanced(K, D, image, balance = 0.0):
    '''This function tries to undistort the image without cutting any of it off.
       Really only works with small images.'''
    input_dim = image.shape[:2]
    output_dim = input_dim

    scaled_K = K*output_dim[0]/input_dim[0]# scale K for new dimensions
    scaled_K[2][2] = 1.0# K[2][2] is always 1.0, regardless of scale
    new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, output_dim, np.eye(3), balance = balance)

    map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, input_dim, cv2.CV_16SC2)
    return cv2.remap(image, map1, map2, interpolation = cv2.INTER_LINEAR, borderMode = cv2.BORDER_CONSTANT)


def load_calib(at_path, image_size_ratio = 1.0):
    try:
        K = np.load(at_path + 'K.npy')*image_size_ratio
        K[2][2] = 1.0
        D = np.load(at_path + 'D.npy')*image_size_ratio
        return K, D
    except FileNotFoundError:
        K, D = create_calib(at_path)
        K *= image_size_ratio
        K[2][2] = 1.0
        D *= image_size_ratio
        return K, D


def create_calib(from_path):
    import glob
    #{define constants}
    chessboard_dims = (6, 9)
    # objp represents the actual layout of a chessboard, which never changes
    objp = np.zeros((1, chessboard_dims[0]*chessboard_dims[1], 3), np.float32)
    objp[0,:,:2] = np.mgrid[0:chessboard_dims[0], 0:chessboard_dims[1]].T.reshape(-1, 2)
    # the following simplify calls to opencv
    subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW

    #{prepare for processing}
    image_dims = None
    objpoints = []# 3d point in real world space
    imgpoints = []# 2d points in image plane
    filenames = glob.glob(from_path + '*.jpg')

    #{attempt to find a chessboard in every image}
    for filename in filenames:
        image = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2GRAY)
        if not image_dims:
            image_dims = image.shape[:2]
        else:
            assert image_dims == image.shape[:2], 'All images must have the same size.'
        # find the chessboard corners
        found, corners = cv2.findChessboardCorners(image, chessboard_dims, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
        if found:
            objpoints.append(objp)
            cv2.cornerSubPix(image, corners, (3, 3), (-1, -1), subpix_criteria)# refine image points
            imgpoints.append(corners)

    #{use chessboard locations to calibrate camera}
    N_OK = len(objpoints)
    K = np.zeros((3, 3))
    D = np.zeros((4, 1))
    rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(N_OK)]
    rms, _, _, _, _ = \
        cv2.fisheye.calibrate(
            objpoints,
            imgpoints,
            image.shape[::-1],
            K,
            D,
            rvecs,
            tvecs,
            calibration_flags,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)
        )

    #{display and save results}
    print('Found {} valid images for calibration'.format(N_OK))
    print('Compatible dimensions: {}'.format(image_dims[1]))
    print('K: {}'.format(K))
    print('D: {}'.format(D))

    np.save(from_path + 'K', K)
    np.save(from_path + 'D', D)

    return K, D
