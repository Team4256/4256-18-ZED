#{ZED}
from ZED import ZED
#{RobotPy}
from networktables import NetworkTables


def stream_position(to):
    def nt_and_exit(message):
        to.putString('Error', message)
        exit(message)
    zed = ZED(error_handler = nt_and_exit)
    zed.enable_tracking()

    translationBin = to.getSubTable('Translation')
    # rotationBin = to.getSubTable('Rotation')

    zed_pose = zcam.PyPose()
    while True:
        to.putBoolean('Running', True)
        try:
            if zed.grab(zcam.PyRuntimeParameters()) == tp.PyERROR_CODE.PySUCCESS:
                # Get the pose of the left eye of the camera with reference to the world frame
                zed.get_position(zed_pose, sl.PyREFERENCE_FRAME.PyREFERENCE_FRAME_WORLD)

                translation = core.PyTranslation()
                tx = round(zed_pose.get_translation(translation).get()[0], 2)
                ty = round(zed_pose.get_translation(translation).get()[1], 2)
                tz = round(zed_pose.get_translation(translation).get()[2], 2)
                translationBin.putNumber('X', tx)
                translationBin.putNumber('Y', ty)
                translationBin.putNumber('Z', tz)

                # orientation = core.PyOrientation()
                # ox = round(zed_pose.get_orientation(orientation).get()[0], 3)
                # oy = round(zed_pose.get_orientation(orientation).get()[1], 3)
                # oz = round(zed_pose.get_orientation(orientation).get()[2], 3)
                # ow = round(zed_pose.get_orientation(orientation).get()[3], 3)
                # rotationBin.putNumber('X', ox)
                # rotationBin.putNumber('Y', oy)
                # rotationBin.putNumber('Z', oz)
                # rotationBin.putNumber('W', ow)

                to.putNumber('Timestamp', zed_pose.timestamp/1e13)
        except:
            to.putBoolean('Running', False)
            zed.close()
            break

if __name__ == "__main__":
    rioURL = '192.168.1.87'#'roborio-4256-frc.local'
    NetworkTables.initialize(server = rioURL)
    stream_position(to = NetworkTables.getTable('ZED'))
