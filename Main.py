#{3RD PARTY}
import cv2
import numpy as np
#{CUSTOM}
from ServerMJPEG import ImageHandler, ThreadedHTTPServer
import Undistort
import Transform2D
import Stitching

#{preparing fisheye cameras}
ELPFisheyeL_film = cv2.VideoCapture(0)
ELPFisheyeR_film = cv2.VideoCapture(1)

ELPFisheyeL_calib_path = 'Resources/ELPFisheyeL/'
ELPFisheyeR_calib_path = 'Resources/ELPFisheyeR/'

def _load_calib(at_path):
    try:
        K = np.load(at_path + 'K.npy')
        D = np.load(at_path + 'D.npy')
        return (True, (K, D))
    except IOError:
        return (False,)

ELPFisheyeL_calib = _load_calib(ELPFisheyeL_calib_path)
ELPFisheyeR_calib = _load_calib(ELPFisheyeR_calib_path)

#{defining other constants}
LR_PinchAmount = 495
Ly_Offset = 0
Ry_Offset = 10
Ltheta = -58
Rtheta = 60
# scale = 1.0# ratio of final image size to source size#TODO implement with pyrDown
# # K and D are tuned to image size, so must adjust based on scale
# K *= scale
# K[2][2] = 1.0
# D *= scale

#{get new frame}
def createSurroundView():
    global ELPFisheyeL_film
    global ELPFisheyeR_film
    global ELPFisheyeL_calib
    global ELPFisheyeR_calib
    global ELPFisheyeL_calib_path
    global ELPFisheyeR_calib_path
    global LR_PinchAmount
    global Ly_Offset
    global Ry_Offset
    global Ltheta
    global Rtheta
    view_left = ELPFisheyeL_film.read()
    view_right = ELPFisheyeR_film.read()

    total_height, total_width = 0, -LR_PinchAmount

    if view_left[0]:# a boolean that says whether camera actually returned an image
        if not ELPFisheyeL_calib[0]:# a boolean that says whether calibration files exist
            #TODO Run Undistort script (...gen_calib(imgpath, savepath))
            ELPFisheyeL_calib = _load_calib(ELPFisheyeL_calib_path)
        (K, D) = ELPFisheyeL_calib[1]
        view_left = Undistort.simple(K, D, view_left[1])
        bird_left = Transform2D.getBirdView(view_left, Transform2D.ELPFisheyeL)#TODO could be sped up by only doing math in getBirdView() once
        final_left = Stitching.rotate(bird_left, Ltheta)#TODO scale parameter
        total_height = max(total_height, final_left.shape[0] + Ly_Offset)
        total_width += final_left.shape[1]

    if view_right[0]:# a boolean that says whether camera actually returned an image
        if not ELPFisheyeR_calib[0]:# a boolean that says whether calibration files exist
            #TODO Run Undistort script (...gen_calib(imgpath, savepath))
            ELPFisheyeR_calib = _load_calib(ELPFisheyeR_calib_path)
        (K, D) = ELPFisheyeR_calib[1]
        view_right = Undistort.simple(K, D, view_right[1])
        bird_right = Transform2D.getBirdView(view_right, Transform2D.ELPFisheyeR)#TODO could be sped up by only doing math in getBirdView() once
        final_right = Stitching.rotate(bird_right, Rtheta)#TODO scale parameter
        total_height = max(total_height, final_right.shape[0] + Ry_Offset)
        total_width += final_right.shape[1]

    if (total_width > 0):# only really need to check one to ensure both are greater than 0
        canvas = np.zeros((total_height, total_width, 3), dtype = 'uint8')
        canvas[Ly_Offset:Ly_Offset + final_left.shape[0], :final_left.shape[1]] = final_left
        canvas_right = canvas[Ry_Offset:Ry_Offset + final_right.shape[0], -final_right.shape[1]:]
        masked = canvas_right == 0
        canvas_right[masked] = final_right[masked]
        return (True, canvas)
    else:
        return (False,)



def streamFromCamera():
    try:
        server = ThreadedHTTPServer(('localhost', 8080), ImageHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


if __name__ == '__main__':
    streamFromCamera()
    ELPFisheyeL_film.release()
    ELPFisheyeR_film.release()
