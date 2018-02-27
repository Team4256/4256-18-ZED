# scale = 1.0# ratio of final image size to source size#TODO implement with pyrDown
# # K and D are tuned to image size, so must adjust based on scale
# K *= scale
# K[2][2] = 1.0
# D *= scale

if __name__ == '__main__':
    #{NON-THREADING RELATED}
    from networktables import NetworkTables

    rioURL = '10.42.56.2'
    NetworkTables.initialize(server = rioURL)
    NetworkTables.setNetworkIdentity('TX2')
    NetworkTables.setUpdateRate(.020)
    table = NetworkTables.getTable('ZED')

    portL, portR = (1, 2)

    #{THREADING RELATED}
    #{import overarching packages}
    from queue import Queue
    from CustomThread import CustomThread
    #{import task-specific classes}
    from Cameras import USB, ZED
    from Stitching import ThreadableStitcher
    from Servers import Web, NT

    #{declare queues}
    queue_cameraL = Queue()
    queue_cameraR = Queue()
    queue_cameraZED = Queue()
    queue_odometry = Queue()
    queue_stitched = Queue()

    #{declare threads}
    thread_cameraL = CustomThread(USB.ThreadableGrabber(portL,
                                                        destination_queue = queue_cameraL,
                                                        calibration_path = 'Resources/ELPFisheyeL/'))
    thread_cameraR = CustomThread(USB.ThreadableGrabber(portR,
                                                        destination_queue = queue_cameraR,
                                                        calibration_path = 'Resources/ELPFisheyeR/'))
    thread_cameraZED = CustomThread(ZED.ThreadableGrabber(queue_cameraZED, queue_odometry))
    thread_stitcher = CustomThread(ThreadableStitcher(queue_cameraL, queue_cameraR, queue_cameraZED, destination_queue = queue_stitched))
    thread_mjpeg = CustomThread(Web.ThreadableMJPGSender(queue_stitched))
    thread_nt = CustomThread(NT.ThreadableOdometrySender(table, queue_odometry))

    #{start threads}
    thread_cameraL.start()
    thread_cameraR.start()
    thread_cameraZED.start()
    thread_stitcher.start()
    thread_mjpeg.start()
    thread_nt.start()

    while True:
        request = input('Type e to exit: ')
        if request == 'e':
            thread_cameraL.stop()
            thread_cameraR.stop()
            thread_cameraZED.stop()
            thread_stitcher.stop()
            thread_mjpeg.stop()
            thread_nt.stop()

            # thread_stitcher.join()
            # thread_cameraL.join()
            # thread_cameraR.join()
            # thread_cameraZED.join()
            # thread_mjpeg.join()
            # thread_nt.join()

            NetworkTables.stopClient()
            break
    print('Done')
