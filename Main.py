from queue import Queue
#{3RD PARTY}
import cv2
import numpy as np



# scale = 1.0# ratio of final image size to source size#TODO implement with pyrDown
# # K and D are tuned to image size, so must adjust based on scale
# K *= scale
# K[2][2] = 1.0
# D *= scale



if __name__ == '__main__':
    camera_queue_L = Queue()
    camera_queue_R = Queue()
    zed_queue_image = Queue()
    zed_queue_odometry = Queue()
    stitching_queue = Queue()


    from CustomThread import CustomThread
    from Stitching import Stitching
    stitching_thread = CustomThread(Stitching(camera_queue_L, camera_queue_R, zed_queue_image, stitching_queue))
    
    from CameraThreads import OpenCV.USB, OpenCV.USB, ZED.ZED
    camera_thread_L = CustomThread(USB(portL, camera_queue_L))
    camera_thread_R = CustomThread(USB(portR, camera_queue_R))
    camera_thread_ZED = CustomThread(ZED(zed_image_queue, zed_odometry_queue))

    from Servers import MJPEG, NetworkTables.NetworkTables
    mjpeg_thread = MJPEG.ThreadedHTTPServer(('localhost', 8080), MJPEG.ImageHandler())


    rioURL = '10.42.56.2'
    NetworkTables.initialize(server = rioURL)
    NetworkTables.setNetworkIdentity('TX2')
    NetworkTables.setUpdateRate(.020)
    table = NetworkTables.getTable('ZED')
    networktables_thread = CustomThread(NetworkTables(table, zed_odometry_queue))

    try:
        stitching_thread.start()
        camera_thread_L.start()
        camera_thread_R.start()
        camera_thread_ZED.start()
        mjpeg_thread.serve_forever()
        networktables_thread.start()
    except KeyboardInterrupt:
        mjpeg_thread.socket.close()
