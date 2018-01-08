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

def stream_position():
    zed = zcam.PyZEDCamera()
    init_params = default_init_params()
    exit_if_failure(zed.open(init_params))# opens camera and checks for errors at the same time

    transform = core.PyTransform()
    tracking_params = zcam.PyTrackingParameters(init_pos = transform)
    exit_if_failure(zed.enable_tracking(tracking_params))# enables tracking and checks for errors at the same time

    # Track the camera position during 1000 frames
    i = 0
    zed_pose = zcam.PyPose()
    while i < 1000:
        if zed.grab(zcam.PyRuntimeParameters()) == tp.PyERROR_CODE.PySUCCESS:
            # Get the pose of the left eye of the camera with reference to the world frame
            zed.get_position(zed_pose, sl.PyREFERENCE_FRAME.PyREFERENCE_FRAME_WORLD)

            # Display the translation and timestamp
            py_translation = core.PyTranslation()
            tx = round(zed_pose.get_translation(py_translation).get()[0], 2)
            ty = round(zed_pose.get_translation(py_translation).get()[1], 2)
            tz = round(zed_pose.get_translation(py_translation).get()[2], 2)
            print("Translation: Tx: {0}, Ty: {1}, Tz {2}, Timestamp: {3}\n".format(tx, ty, tz, zed_pose.timestamp))

            # Display the orientation quaternion
            #py_orientation = core.PyOrientation()
            #ox = round(zed_pose.get_orientation(py_orientation).get()[0], 3)
            #oy = round(zed_pose.get_orientation(py_orientation).get()[1], 3)
            #oz = round(zed_pose.get_orientation(py_orientation).get()[2], 3)
            #ow = round(zed_pose.get_orientation(py_orientation).get()[3], 3)
            #print("Orientation: Ox: {0}, Oy: {1}, Oz {2}, Ow: {3}\n".format(ox, oy, oz, ow))

            i = i + 1

    # Close the camera
    zed.close()

if __name__ == "__main__":
    rioURL = '192.168.1.87'#'roborio-4256-frc.local'
    NetworkTables.initialize(server = rioURL)
    portal = NetworkTables.getTable('ZED')
    portal.putBoolean("test", True)
    stream_position()
