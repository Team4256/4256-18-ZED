import cv2# only necessary for pyrDown
from ..ZED import ZED as camera
class ZED(object):
    def __init__(self, image_queue, odometry_queue):
        self.image_queue = image_queue
        self.odometry_queue = odometry_queue
        self.camera = camera()
        camera.enable_tracking()
        camera.enable_rgb()

    def run(self):
        self.camera.grab()
        new_position = self.camera.position()
        if new_position is not None:
            self.odometry_queue.put_nowait(new_position)

        new_rgb = cv2.pyrDown(zed.numpy_rgb())# experiment
        if new_rgb is not None:
            self.image_queue.put_nowait(new_rgb)

    def release(self):
        self.camera.camera.close()
