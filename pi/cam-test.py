import cv2 as cv
from cv2 import COLOR_BGR2RGB
import os
import time
import numpy as np

# from picamera.array import PiRGBArray
# from picamera import PiCamera

# camera=PiCamera(sensor_mode=2)
# camera.resolution=(2592,1944)
# camera.exposure_compensation=-6
# camera.meter_mode='backlit'
# camera.framerate=60

RECORD_VIDEO = False

ref = "stars"
script_path = os.path.dirname(os.path.realpath(__file__))
proj_path = os.path.dirname(script_path)
media_path = os.path.join(proj_path, "media")

vid = cv.VideoCapture(0, cv.CAP_V4L2)
vid.set(cv.CAP_PROP_FRAME_WIDTH, 960) #2592
vid.set(cv.CAP_PROP_FRAME_HEIGHT, 720) #1944

def monitor(vid): 

    # vid = cv.VideoCapture(os.path.join(media_path, f"{ref}-1.h264"))
    
    vid_out1 = None
    print(vid.get(cv.CAP_PROP_FRAME_WIDTH), vid.get(cv.CAP_PROP_FRAME_HEIGHT))

    framenum = 0
    scale_factor = 1

    fourcc = cv.VideoWriter_fourcc(*'XVID')
    # fourcc = cv.VideoWriter_fourcc(*'H264')
    tEnd = time.time()

    while vid.isOpened():

        t4 = time.time()
        
        framenum +=1
        
        ret, img1 = vid.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

        out_img_disp = cv.resize(img1, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
        cv.putText(out_img_disp,"{:.2f} fps".format(1/(t4-tEnd)),(10,25),cv.FONT_HERSHEY_COMPLEX,0.5,(25,255,255),1)
        cv.imshow("video", out_img_disp)
        
        if RECORD_VIDEO:
            if vid_out1 is None:
                w, h = img1.shape[:2]
                vid_num = 0
                vid_out_path = os.path.join(media_path, f"{ref}-capture-{vid_num}.avi")
                while os.path.exists(vid_out_path):
                    vid_num += 1
                    vid_out_path = os.path.join(media_path, f"{ref}-capture-{vid_num}.avi")
                vid_out1 = cv.VideoWriter(vid_out_path, fourcc, 20.0, (h, w))
                print(vid_out1.isOpened(), img1.shape[:2], vid_out_path)

            vid_out1.write(img1)

        k = cv.waitKey(delay=1)
        if k == 'q':
            break

        if framenum % 60 == 0:
            print("FPS = {:.2f}".format(1/(t4-tEnd)))

        tEnd = t4

try:
    monitor(vid)
except KeyboardInterrupt:
    RECORD_VIDEO = True
    try:
        monitor(vid)
    except KeyboardInterrupt:
        pass

# print("ORB detected and computed in {:.3f}s".format(t1-t0), "\t Matching in {:.3f}s".format(t2-t1), "\t Homography in {:.3f}s".format(t4-t3))
# fig1, axes = plt.subplots(1,2)
# plt.subplots_adjust(0.02,0.1,0.98,0.9)
# # axes.imshow(cv.cvtColor(reference_img, cv.COLOR_BGR2RGB))
# axes[0].imshow(cv.cvtColor(out_img,cv.COLOR_BGR2RGB))
# axes[1].imshow(cv.cvtColor(match_img,cv.COLOR_BGR2RGB))
# axes[0].axis('off')
# axes[1].axis('off')
# plt.show()

try:
    vid.release()
    vid_out1.release()
except:
    pass
