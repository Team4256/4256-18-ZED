#{ZED}
from ZED import ZED
#{RobotPy}
from networktables import NetworkTables
#{OpenCV}
import cv2


def stream_position(to):
    zed = ZED()
    zed.enable_tracking()
    zed.enable_rgb()

    positionBin = to.getSubTable('Position')

    while True:
        try:
            zed.grab()
            new_position = zed.position()
            if new_position is not None:
                positionBin.putNumber('X', -round(new_position[0], 3))
                positionBin.putNumber('Y', -round(new_position[1], 3))
                positionBin.putNumber('Z', round(new_position[2], 3))
                positionBin.putNumber('Confidence', zed.pose.pose_confidence)

                positionBin.putNumber('Timestamp', zed.pose.timestamp/1e13)
                positionBin.putString('Tracking Status', zed.tracking_status)

            new_rgb = cv2.pyrDown(zed.numpy_rgb())
            if new_rgb is not None:
                cv2.imshow('Live', new_rgb)
                cv2.waitKey(5)

            to.putString('Overall Status', zed.overall_status)

        except KeyboardInterrupt:
            positionBin.clearPersistent('X')
            positionBin.clearPersistent('Y')
            positionBin.clearPersistent('Z')
            positionBin.clearPersistent('Confidence')
            positionBin.clearPersistent('Timestamp')
            positionBin.clearPersistent('Tracking Status')
            to.clearPersistent('Overall Status')
            to.deleteAllEntries()
            zed.camera.close()
            break

if __name__ == '__main__':
    rioURL = '10.42.56.2'
    NetworkTables.initialize(server = rioURL)
    NetworkTables.setNetworkIdentity('TX2')
    NetworkTables.setUpdateRate(.020)
    stream_position(to = NetworkTables.getTable('ZED'))
    NetworkTables.stopClient()
