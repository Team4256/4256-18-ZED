#{ZED}
from ZED import ZED
#{RobotPy}
from networktables import NetworkTables
#{OpenCV}
import cv2


def stream_position(to):
    zed = ZED()
    zed.enable_tracking()
    zed.enable_video()
    zed.enable_cloud()

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

            new_image = zed.numpy_image()
            if new_image is not None:
                cv2.imshow('Live', new_image)
                cv2.waitKey(5)

            new_cloud = zed.numpy_cloud()

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
