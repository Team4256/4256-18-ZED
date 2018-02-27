# 4256-18-ZED

### Threading model
The Python vision code runs six threads which communicate with each other using Python's MPMC `queue.Queue`.  Threads are encapsulated around classes, and execute their `run()` methods in a loop.  Here is a list of the threads, their functions, and the queues they use to communicate:

* `ZED()`
   * Inputs: The ZED hardware
   * Outputs: `zed_odometry_queue`, `zed_image_queue`
   * Purpose: This runs in a tight loop getting data from the ZED and pushing it to the other threads.

* `USB(input_camera, destination_queue)` (two threads, one each for left and right cameras)
   * Inputs: the specified input camera
   * Outputs: the specified destination queue (`camera_queue_L` or `camera_queue_R`)
   * Purpose: Reads a single camera using OpenCV and posts its image to a dedicated queue in a tight loop.  OpenCV reads the camera at 30Hz, so there's a lot of waiting in this loop.  There are two USB threads...one for the left-facing camera and one for the right-facing one.

* `Stitching()`
   * Inputs: `zed_image_queue`, `camera_queue_L`, `camera_queue_R`
   * Outputs: `stitched_image_queue`
   * Purpose: Process raw ZED binocular images into a "stiched" overhead image

* `NetworkTables()`
   * Inputs: `zed_odometry_queue`
   * Outputs: NetworkTables
   * Purpose: Take the latest updates from `zed_odometry_queue` and post them to the global NetworkTables.

* `MJPEG.ThreadedHTTPServer()`
   * Inputs: `stitched_image_queue`
   * Outputs: supports a `GET` handler to send the three up-to-date images to the drive station
   * Purpose: provide up-to-date imagery to the drive station
