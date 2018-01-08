#{ZED}
import pyzed.camera as zcam
import pyzed.defines as sl
import pyzed.types as tp
import pyzed.core as core

def default_init_params():
    params = zcam.PyInitParameters()# creates a place to store param
    params.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD720# HD720, 60 fps
    params.coordinate_system = sl.PyCOORDINATE_SYSTEM.PyCOORDINATE_SYSTEM_RIGHT_HANDED_Z_UP
    params.coordinate_units = sl.PyUNIT.PyUNIT_METER
    return params

class ZED(object):
    def __init__(self, error_handler = exit):
        self.camera = zcam.PyZEDCamera()
        def check_status(operation):
            if operation != tp.PyERROR_CODE.PySUCCESS:
                error_handler(sl.errorCode2str(operation))
        self.check_status = check_status
        self.check_status(self.camera.open(default_init_params()))# opens camera and checks for errors at the same time

    def enable_tracking(self):
        transform = core.PyTransform()
        params = zcam.PyTrackingParameters(init_pos = transform)
        self.check_status(self.camera.enable_tracking(params))# enables tracking and checks for errors at the same time
