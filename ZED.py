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
#{numpy}
from numpy import ctypeslib

def default_init_params():
    params = zcam.PyInitParameters()# creates a place to store param
    params.camera_resolution = sl.PyRESOLUTION.PyRESOLUTION_HD720
    params.camera_fps = 60
    # options are HD2K (15fps), HD1080 (max 30fps), HD720 (max 60fps), WVGA (max 100fps)
    params.depth_mode = sl.PyDEPTH_MODE.PyDEPTH_MODE_PERFORMANCE
    # options are NONE, PERFORMANCE, MEDIUM, QUALITY, ULTRA
    params.depth_stabilization = True
    params.depth_minimum_distance = 7
    # less than 10, lower numbers increase grab() time
    params.coordinate_system = sl.PyCOORDINATE_SYSTEM.PyCOORDINATE_SYSTEM_RIGHT_HANDED_Z_UP
    params.coordinate_units = sl.PyUNIT.PyUNIT_FOOT
    # options are MILLIMETER, CENTIMETER, METER, INCH, FOOT
    return params

def default_tracking_params():
    params = zcam.PyTrackingParameters(init_pos = core.PyTransform())
    params.enable_spatial_memory = True
    #params.enable_pose_smoothing = False # Listed in documentation but doesn't work
    return params


class ZED(object):
    def __init__(self):
        self.camera = zcam.PyZEDCamera()
        self.overall_status = self.camera.open(default_init_params())
        # opens camera and updates overall_status at the same time
        self.tracking_status = 'Disabled'
        self.video_status = 'Disabled'
        self.cloud_status = 'Disabled'

    """load_area should be False or a file path string"""
    def enable_tracking(self, load_area = False):
        params = default_tracking_params()
        if load_area is not False:
            params.area_file_path = load_area
        self.overall_status = self.camera.enable_tracking(params)
        # enables tracking and updates overall_status at the same time
        self.pose = zcam.PyPose()
        self.tracking_status = 'Enabled'

    """save_area should be False or a file path string"""
    def disable_tracking(self, save_area = False):
        if save_area is not False:
            self.camera.disable_tracking(save_area)
        else:
            self.camera.disable_tracking()
        self.tracking_status = 'Disabled'

    def enable_video(self):
        self.image = core.PyMat()
        self.video_status = 'Enabled'

    def disable_video(self):
        self.video_status = 'Disabled'

    def enable_cloud(self):
        self.cloud = core.PyMat()
        self.cloud_status = 'Enabled'

    def disable_cloud(self):
        self.cloud_status = 'Disabled'

    def grab(self):
        self.overall_status = self.camera.grab(zcam.PyRuntimeParameters())
        if self._overall_status == tp.PyERROR_CODE.PySUCCESS:
            if self.tracking_status is not 'Disabled':
                self.tracking_status = self.camera.get_position(self.pose, sl.PyREFERENCE_FRAME.PyREFERENCE_FRAME_WORLD)
                # locates left camera with respect to world
            if self.video_status is not 'Disabled':
                self.video_status = self.camera.retrieve_image(self.image, sl.PyVIEW.PyVIEW_LEFT)#, core.PyMEM.PyMEM_CPU, width = 0, height = 0)
                # GPU mode doesn't work, width and height of 0 means default
                # from left camera
            if self.cloud_status is not 'Disabled':
                self.cloud_status = self.camera.retrieve_measure(self.cloud, sl.PyMEASURE.PyMEASURE_XYZBGRA)#, core.PyMEM.PyMEM_CPU, width = 0, height = 0)
                # GPU mode doesn't work, width and height of 0 means default
                # from left camera

    def position(self):
        if self._tracking_status == sl.PyTRACKING_STATE.PyTRACKING_STATE_OK:
            return self.pose.get_translation(core.PyTranslation()).get()
        else:
            return None

    def orientation(self):
        if self._tracking_status == sl.PyTRACKING_STATE.PyTRACKING_STATE_OK:
            return self.pose.get_orientation(core.PyOrientation()).get()
        else:
            return None

    def numpy_image(self):
        if self._video_status == tp.PyERROR_CODE.PySUCCESS:
            return self.image.get_data()
        else:
            return None

    def numpy_cloud(self):
        if self._cloud_status == tp.PyERROR_CODE.PySUCCESS:
            return self.cloud.get_data()
        else:
            return None


    @property
    # this denotes a "getter," meaning the function below generates the value of self.overall_status
    def overall_status(self):
        return str(self._overall_status)

    @overall_status.setter
    # this denotes a "setter," meaning the function below assigns a new value to self.overall_status
    def overall_status(self, update):
        self._overall_status = update

    @property
    def tracking_status(self):
        return str(self._tracking_status)

    @tracking_status.setter
    def tracking_status(self, update):
        self._tracking_status = update

    @property
    def video_status(self):
        return str(self._video_status)

    @video_status.setter
    def video_status(self, update):
        self._video_status = update

    @property
    def cloud_status(self):
        return str(self._cloud_status)

    @cloud_status.setter
    def cloud_status(self, update):
        self._cloud_status = update

