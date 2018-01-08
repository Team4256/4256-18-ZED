#{ZED}
import pyzed.camera as zcam
import pyzed.defines as sl
import pyzed.types as tp
import pyzed.core as core
#{RobotPy}
from networktables import NetworkTables

def exit_if_failure(zed_status):
    if zed_status != tp.PyERROR_CODE.PySUCCESS:
        exit(1)

def default_init_params():
    params = zcam.PyInitParameters()# creates a place to store param
    params.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD720# HD720, 60 fps
    params.coordinate_system = sl.PyCOORDINATE_SYSTEM.PyCOORDINATE_SYSTEM_RIGHT_HANDED_Z_UP
    params.coordinate_units = sl.PyUNIT.PyUNIT_METER
    return params

def stream_position(to):
    zed = zcam.PyZEDCamera()
    init_params = default_init_params()
    exit_if_failure(zed.open(init_params))# opens camera and checks for errors at the same time

    transform = core.PyTransform()
    tracking_params = zcam.PyTrackingParameters(init_pos = transform)
    exit_if_failure(zed.enable_tracking(tracking_params))# enables tracking and checks for errors at the same time

    translationBin = to.getSubTable('Translation')
    # rotationBin = to.getSubTable('Rotation')

    zed_pose = zcam.PyPose()
    while True:
        try:
            if zed.grab(zcam.PyRuntimeParameters()) == tp.PyERROR_CODE.PySUCCESS:
                # Get the pose of the left eye of the camera with reference to the world frame
                zed.get_position(zed_pose, sl.PyREFERENCE_FRAME.PyREFERENCE_FRAME_WORLD)

                translation = core.PyTranslation()
                tx = round(zed_pose.get_translation(translation).get()[0], 2)
                ty = round(zed_pose.get_translation(translation).get()[1], 2)
                tz = round(zed_pose.get_translation(translation).get()[2], 2)
                translationBin.putNumber('x', tx)
                translationBin.putNumber('y', ty)
                translationBin.putNumber('z', tz)

                # orientation = core.PyOrientation()
                # ox = round(zed_pose.get_orientation(orientation).get()[0], 3)
                # oy = round(zed_pose.get_orientation(orientation).get()[1], 3)
                # oz = round(zed_pose.get_orientation(orientation).get()[2], 3)
                # ow = round(zed_pose.get_orientation(orientation).get()[3], 3)
                # rotationBin.putNumber('x', ox)
                # rotationBin.putNumber('y', oy)
                # rotationBin.putNumber('z', oz)
                # rotationBin.putNumber('w', ow)

                to.putNumber('timestamp', zed_pose.timestamp)
        except:
            zed.close()
            break

if __name__ == "__main__":
    rioURL = '192.168.1.87'#'roborio-4256-frc.local'
    NetworkTables.initialize(server = rioURL)
    table = NetworkTables.getTable('ZED')
    stream_position(to = table)
