"""
PySUCCESS : standard code
PyERROR_CODE_FAILURE : standard code
PyERROR_CODE_NO_GPU_COMPATIBLE
PyERROR_CODE_NOT_ENOUGH_GPUMEM
PyERROR_CODE_CAMERA_NOT_DETECTED
PyERROR_CODE_INVALID_RESOLUTION
PyERROR_CODE_LOW_USB_BANDWIDTH : occurs when using ZED through USB 2.0
PyERROR_CODE_CALIBRATION_FILE_NOT_AVAILABLE : use ZED Explorer to make one
PyERROR_CODE_INVALID_SVO_FILE
PyERROR_CODE_SVO_RECORDING_ERROR
PyERROR_CODE_INVALID_COORDINATE_SYSTEM
PyERROR_CODE_INVALID_FIRMWARE
PyERROR_CODE_NOT_A_NEW_FRAME : specific to grab()
PyERROR_CODE_CUDA_ERROR : specific to grab()
PyERROR_CODE_CAMERA_NOT_INITIALIZED : specific to grab(), fix by calling open()
PyERROR_CODE_NVIDIA_DRIVER_OUT_OF_DATE
PyERROR_CODE_INVALID_FUNCTION_CALL : usually fix by calling open()
PyERROR_CODE_CORRUPTED_SDK_INSTALLATION
PyERROR_CODE_LAST
"""
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
    def __init__(self):
        self.camera = zcam.PyZEDCamera()
        self.overall_status = self.camera.open(default_init_params())# opens camera and updates overall_status at the same time
        self.pose = None# just declaring for later use

    def enable_tracking(self):
        transform = core.PyTransform()
        params = zcam.PyTrackingParameters(init_pos = transform)
        self.overall_status = self.camera.enable_tracking(params)# enables tracking and updates overall_status at the same time
        self.pose = zcam.PyPose()

    def grab(self):
        self.overall_status = self.camera.grab(zcam.PyRuntimeParameters())
        if self._overall_status == tp.PyERROR_CODE.PySUCCESS:
            print(self.camera.get_position(self.pose, sl.PyREFERENCE_FRAME.PyREFERENCE_FRAME_WORLD))# locates left camera eye with respect to world

    def position(self):
        if self._overall_status == tp.PyERROR_CODE.PySUCCESS:
            return self.pose.get_translation(core.PyTranslation()).get()
        else:
            return None

    def orientation(self):
        if self._overall_status == tp.PyERROR_CODE.PySUCCESS:
            return self.pose.get_orientation(core.PyOrientation()).get()
        else:
            return None

    @property# this denotes a "getter," meaning the function below generates the value of self.overall_status
    def overall_status(self):
        return sl.errorCode2str(self._overall_status)

    @overall_status.setter# this denotes a "setter," meaning the function below assigns a new value to self.overall_status
    def overall_status(self, update):
        self._overall_status = update
