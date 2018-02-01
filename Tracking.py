#{ZED}
from ZED import ZED
import Cloud
#{RobotPy}
from networktables import NetworkTables
#{OpenCV}
import cv2
import numpy as np# TODO shouldn't need to import this here


def stream_position(to):
    zed = ZED()
    zed.enable_tracking()
    zed.enable_rgb()
    zed.enable_depth()

    positionBin = to.getSubTable('Position')

    while True:
        try:
            zed.grab()
            new_position = zed.position()
            if new_position is not None:
                positionBin.putNumber('X', round(new_position[0], 3))
                positionBin.putNumber('Y', round(new_position[1], 3))
                positionBin.putNumber('Z', round(new_position[2], 3))

                #positionBin.putNumber('Timestamp', zed.pose.timestamp/1e13)
                positionBin.putString('Tracking Status', zed.tracking_status)

            new_rgb = cv2.pyrDown(zed.numpy_rgb())
            if new_rgb is not None:
                cv2.imshow('Live', new_rgb)
                cv2.waitKey(5)

            new_depth = cv2.pyrDown(zed.numpy_depth())
            if new_depth is not None:
                new_depth[~np.isfinite(new_depth)] = 0
                new_depth *= 255/new_depth.max()
                top = Cloud.get_top_from_front(new_depth)
                cv2.imshow('Depth', new_depth.astype('uint8')[:,:,None])
                cv2.imshow('Bird', top.astype('uint8'))

            to.putString('Overall Status', zed.overall_status)

        except KeyboardInterrupt:
            zed.camera.close()
            break

if __name__ == '__main__':
    rioURL = '192.168.0.189'#'10.42.56.2'
    NetworkTables.initialize(server = rioURL)
    #NetworkTables.startClientTeam(4256, port = 1735)
    NetworkTables.setUpdateRate(.020)
    stream_position(to = NetworkTables.getTable('ZED'))
    NetworkTables.stopClient()
