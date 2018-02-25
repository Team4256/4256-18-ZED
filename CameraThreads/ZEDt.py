import cv2# only necessary for pyrDown

# from ZED import ZED as camera# comment out for non-TX2
class ZEDt(object):
    def __init__(self, image_queue, odometry_queue):
        self.image_queue = image_queue
        self.odometry_queue = odometry_queue
        # comment out for non-TX2
        # self.camera = camera()
        # camera.enable_tracking()
        # camera.enable_rgb()

    def run(self):
        while True:
            # comment out for non-TX2
            # self.camera.grab()
            # new_position = self.camera.position()
            # if new_position is not None:
            #     new_position.append(self.camera.pose.pose_confidence)
            #     new_position.append(self.camera.pose.timestamp/1e13)
            #     new_position.append(self.camera.tracking_status)
            #
            #     self.odometry_queue.put(new_position)

            new_rgb = cv2.pyrDown(cv2.imread('C:/Users/h_shively/0eveloper/workspace/{git, collab} 4256-18-ZED/Resources/ZED/Sample RGB.jpg'))#cv2.pyrDown(zed.numpy_rgb())# experiment
            if new_rgb is not None:
                self.image_queue.put(new_rgb)

    def release(self):
        self.camera.camera.close()
