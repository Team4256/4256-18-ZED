#{ZED}
from ZED import ZED
#{RobotPy}
from networktables import NetworkTables


def stream_position(to):
    zed = ZED()
    zed.enable_tracking()

    positionBin = to.getSubTable('Position')

    while True:
        try:
            zed.grab()
            new_position = zed.position()
            if new_position is not None:
                positionBin.putNumber('X', round(new_position[0], 3))
                positionBin.putNumber('Y', round(new_position[1], 3))
                positionBin.putNumber('Z', round(new_position[2], 3))

                positionBin.putNumber('Timestamp', zed.pose.timestamp/1e13)
                positionBin.putString('Tracking Status', zed.tracking_status)

            to.putString('Overall Status', zed.overall_status)

        except:
            zed.camera.close()
            break

if __name__ == '__main__':
    rioURL = '192.168.0.195'#'roborio-4256-frc.local'
    NetworkTables.initialize(server = rioURL)
    stream_position(to = NetworkTables.getTable('ZED'))
