from queue import Queue
#{3RD PARTY}
import cv2
import numpy as np



# scale = 1.0# ratio of final image size to source size#TODO implement with pyrDown
# # K and D are tuned to image size, so must adjust based on scale
# K *= scale
# K[2][2] = 1.0
# D *= scale

zed_odometry_queue = Queue()
zed_image_queue = Queue()
stitched_image_queue = Queue()
left_image_queue = Queue()
right_image_queue = Queue()




if __name__ == '__main__':
    from CustomThread import CustomThread
    from Stitching import Stitching
    stitching_thread = CustomThread(Stitching())
    from CameraThreads import Left.Left, Right.Right, ZED.ZED
    camera_thread_L = CustomThread(Left())
    camera_thread_R = CustomThread(Right())
    camera_thread_ZED = CustomThread(ZED())
    from Servers import MJPEG, NetworkTables.NetworkTables
    mjpeg_thread = MJPEG.ThreadedHTTPServer(('localhost', 8080), MJPEG.ImageHandler())
    networktables_thread = CustomThread(NetworkTables())

    try:
        stitching_thread.start()
        camera_thread_L.start()
        camera_thread_R.start()
        camera_thread_ZED.start()
        mjpeg_thread.serve_forever()
        networktables_thread.start()
    except KeyboardInterrupt:
        mjpeg_thread.socket.close()
