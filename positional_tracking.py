#{ZED}
from ZED import ZED
#{RobotPy}
from networktables import NetworkTables


def stream_position(to):
    zed = ZED()
    zed.enable_tracking()

    translationBin = to.getSubTable('Translation')
    # rotationBin = to.getSubTable('Rotation')

    while True:
        try:
            zed.grab()
            new_position = zed.position()
            if new_position is not None:
                translationBin.putNumber('X', round(new_position[0], 3))
                translationBin.putNumber('Y', round(new_position[1], 3))
                translationBin.putNumber('Z', round(new_position[2], 3))

            # new_orientation = zed.orientation()
            #     rotationBin.putNumber('X', round(new_position[0], 2))
            #     rotationBin.putNumber('Y', round(new_position[1], 2))
            #     rotationBin.putNumber('Z', round(new_position[2], 2))
            #     rotationBin.putNumber('W', round(new_position[3], 2))

                # to.putNumber('Timestamp', zed_pose.timestamp/1e13)
        except:
            zed.camera.close()
            break

if __name__ == "__main__":
    rioURL = '192.168.1.87'#'roborio-4256-frc.local'
    NetworkTables.initialize(server = rioURL)
    stream_position(to = NetworkTables.getTable('ZED'))
