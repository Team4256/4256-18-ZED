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
"""
"""
PyTRACKING_STATE_SEARCHING
PyTRACKING_STATE_OK
PyTRACKING_STATE_OFF
PyTRACKING_STATE_FPS_TOO_LOW
"""
#{ZED}
import pyzed.camera as zcam
import pyzed.defines as sl
import pyzed.types as tp
import pyzed.core as core
#{OpenCV}
# from cv2 import pyrDown as shrink

def default_init_params():
    params = zcam.PyInitParameters()# creates a place to store params
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
        self.rgb_status = 'Disabled'
        self.depth_status = 'Disabled'

    """load_area should be False or a file path string"""
    def enable_tracking(self, load_area = False):
        params = default_tracking_params()
        if load_area is not False:
            params.area_file_path = load_area
        self.overall_status = self.camera.enable_tracking(params)
        # enables tracking and updates overall_status at the same time
        translation = core.PyTranslation()
        translation.init_vector(-0.68, 0.0, 0.0)
        transform = core.PyTransform()
        transform.set_translation(translation)

        self.pose = zcam.PyPose()
        self.pose.init_transform(transform)
        self.tracking_status = 'Enabled'

    """save_area should be False or a file path string"""
    def disable_tracking(self, save_area = False):
        if save_area is not False:
            self.camera.disable_tracking(save_area)
        else:
            self.camera.disable_tracking()
        self.tracking_status = 'Disabled'

    def enable_rgb(self):
        self.rgb = core.PyMat()
        self.rgb_status = 'Enabled'

    def disable_rgb(self):
        self.rgb_status = 'Disabled'

    def enable_depth(self):
        self.depth = core.PyMat()
        self.depth_status = 'Enabled'

    def disable_depth(self):
        self.depth_status = 'Disabled'

    def grab(self):
        self.overall_status = self.camera.grab(zcam.PyRuntimeParameters(sensing_mode = sl.PySENSING_MODE.PySENSING_MODE_STANDARD))
        # options are STANDARD, FILL
        if self._overall_status == tp.PyERROR_CODE.PySUCCESS:
            if self.tracking_status is not 'Disabled':
                self.tracking_status = self.camera.get_position(self.pose, sl.PyREFERENCE_FRAME.PyREFERENCE_FRAME_WORLD)
                # locates left camera with respect to world
            if self.rgb_status is not 'Disabled':
                self.rgb_status = self.camera.retrieve_image(self.rgb, sl.PyVIEW.PyVIEW_LEFT)#, core.PyMEM.PyMEM_CPU, width = 0, height = 0)
                # GPU mode doesn't work, width and height of 0 means default
                # from left camera
            if self.depth_status is not 'Disabled':
                self.depth_status = self.camera.retrieve_measure(self.depth, sl.PyMEASURE.PyMEASURE_DEPTH)#, core.PyMEM.PyMEM_CPU, width = 0, height = 0)
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

    def numpy_rgb(self):
        if self._rgb_status == tp.PyERROR_CODE.PySUCCESS:
            return self.rgb.get_data()
        else:
            return None

    def numpy_depth(self):
        if self._depth_status == tp.PyERROR_CODE.PySUCCESS:
            return self.depth.get_data()
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
    def rgb_status(self):
        return str(self._rgb_status)

    @rgb_status.setter
    def rgb_status(self, update):
        self._rgb_status = update

    @property
    def depth_status(self):
        return str(self._depth_status)

    @depth_status.setter
    def depth_status(self, update):
        self._depth_status = update


class ThreadableGrabber(object):
    def __init__(self, image_queue, odometry_queue):
        self.image_queue = image_queue
        self.odometry_queue = odometry_queue

        self.zed = ZED()
        self.zed.enable_tracking()
        # self.zed.enable_rgb()

        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            self.zed.grab()
            new_position = self.zed.position()
            if new_position is not None:
                new_position = new_position.tolist()
                new_position.append(self.zed.pose.pose_confidence)
                new_position.append(self.zed.pose.timestamp/1e6)
                new_position.append(self.zed.tracking_status)

                self.odometry_queue.put(new_position)

            # new_rgb = self.zed.numpy_rgb()
            # if new_rgb is not None:
            #     self.image_queue.put(shrink(new_rgb))#TODO experiment with image size

        self._release()

    def _release(self):
        self.zed.camera.close()

    def stop(self):
        self.enabled = False
