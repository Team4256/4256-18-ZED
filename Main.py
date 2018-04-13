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
    queue_cubes = Queue()

    #{initialize cameras}
    cameraL = USB.USB(portL, 'Resources/ELPFisheyeL/')
    cameraR = USB.USB(portR, 'Resources/ELPFisheyeR/')

    #{declare threads}
    thread_cameraZED = CustomThread(ZED.ThreadableGrabber(queue_cameraZED, queue_odometry))
    thread_stitcher = CustomThread(ThreadableStitcher(cameraL, cameraR, queue_stitched, queue_cubes))
    thread_mjpeg = CustomThread(Web.ThreadableMJPGSender(queue_stitched, robot_data))
    thread_nt_odometry = CustomThread(NT.ThreadableOdometrySender(table, queue_odometry))
    thread_nt_cubes = CustomThread(NT.ThreadableCubeSender(table, queue_cubes))

    #{start threads}
    thread_cameraZED.start()
    thread_stitcher.start()
    thread_mjpeg.start()
    thread_nt_odometry.start()
    thread_nt_cubes.start()
    zed_running = True

    from time import sleep
    while True:
        try:
            #{stopping ZED when it is no longer needed}
            if not table.getBoolean('Enable Odometry', True):
                if zed_running:
                    thread_cameraZED.stop()
                    thread_cameraZED.join()
                    zed_running = False

            sleep(1.0)

        except KeyboardInterrupt:
            #{ending the program entirely}
            thread_stitcher.stop()
            thread_mjpeg.stop()
            thread_nt_odometry.stop()
            thread_nt_cubes.stop()
            thread_stitcher.join()
            thread_mjpeg.join()

            if zed_running:
                thread_cameraZED.stop()
                thread_cameraZED.join()
                zed_running = False

            # Wake up thread_nt's if they're stuck in a get()
            queue_odometry.put(None)
            queue_cubes.put(None)
            thread_nt_odometry.join()
            thread_nt_cubes.join()

            NetworkTables.stopClient()
            break

    print('--------program terminated--------')
