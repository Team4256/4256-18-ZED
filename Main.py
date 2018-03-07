if __name__ == '__main__':
    #{NON-THREADING RELATED}
    from networktables import NetworkTables

    rioURL = '10.42.56.2'
    NetworkTables.initialize(server = rioURL)
    NetworkTables.setNetworkIdentity('TX2')
    NetworkTables.setUpdateRate(.020)
    table = NetworkTables.getTable('ZED')
    robot_data = NetworkTables.getTable('Faraday')

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
    queue_cameraZED = Queue()
    queue_odometry = Queue()
    queue_stitched = Queue()

    #{initialize cameras}
    cameraL = USB.USB(portL, 'Resources/ELPFisheyeL/')
    cameraR = USB.USB(portR, 'Resources/ELPFisheyeR/')

    #{declare threads}
    thread_cameraZED = CustomThread(ZED.ThreadableGrabber(queue_cameraZED, queue_odometry))
    thread_stitcher = CustomThread(ThreadableStitcher(cameraL, cameraR, destination_queue = queue_stitched))
    thread_mjpeg = CustomThread(Web.ThreadableMJPGSender(queue_stitched))
    thread_nt = CustomThread(NT.ThreadableOdometrySender(table, queue_odometry))

    #{start threads}
    thread_cameraZED.start()
    thread_stitcher.start()
    thread_mjpeg.start()
    thread_nt.start()
    zed_running = True

    import time
    while True:
        try:
            #{stopping ZED when it is no longer needed}
            if robot_data.getBoolean('Enable Odometry', True):
                if not zed_running:
                    thread_cameraZED.start()
                    zed_running = True
            else:
                if zed_running:
                    thread_cameraZED.stop()
                    zed_running = False

            time.sleep(1.0)

        except KeyboardInterrupt:
            #{ending the program entirely}
            thread_cameraZED.stop()
            thread_stitcher.stop()
            thread_mjpeg.stop()
            thread_nt.stop()

            thread_cameraZED.join()
            thread_stitcher.join()
            thread_mjpeg.join()
            # Wake up thread_nt if it's stuck in a get()
            queue_odometry.put(None)
            thread_nt.join()

            NetworkTables.stopClient()
            break

    print('Done')
