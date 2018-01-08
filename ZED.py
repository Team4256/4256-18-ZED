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
    def __init__(self, nt_log = None):
        self.camera = zcam.PyZEDCamera()
        if nt_log is not None:
            def exit_if_failure(status, log_message):
                if status != tp.PyERROR_CODE.PySUCCESS:
                    nt_log.putString('Failure Type', log_message)
                    exit(1)
        else:
            def exit_if_failure(status, log_message):
                if status != tp.PyERROR_CODE.PySUCCESS:
                    exit(1)
        self.exit_if_failure = exit_if_failure
        self.exit_if_failure(self.camera.open(default_init_params()), 'Failed to open camera.')# opens camera and checks for errors at the same time

    def enable_tracking(self):
        transform = core.PyTransform()
        params = zcam.PyTrackingParameters(init_pos = transform)
        self.exit_if_failure(self.camera.enable_tracking(params), 'Failed to enable tracking.')# enables tracking and checks for errors at the same time
