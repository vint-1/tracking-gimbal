import cv2 as cv
from cv2 import COLOR_BGR2RGB
import os
import time
import numpy as np
import matplotlib.pyplot as plt

# from picamera.array import PiRGBArray
# from picamera import PiCamera

# camera=PiCamera(sensor_mode=2)
# camera.resolution=(2592,1944)
# camera.exposure_compensation=-6
# camera.meter_mode='backlit'
# camera.framerate=60

ref_ext = "jpg"
ref = "stars-capture"

ext = "png"

RECORD_VIDEO = True

script_path = os.path.dirname(os.path.realpath(__file__))
proj_path = os.path.dirname(script_path)
media_path = os.path.join(proj_path, "media", "stars", "first-light")

vid = cv.VideoCapture(os.path.join(media_path, f"{ref}-0.avi"))

# vid = cv.VideoCapture(0, cv.CAP_V4L2)
# vid.set(cv.CAP_PROP_FRAME_WIDTH, 960) #2592
# vid.set(cv.CAP_PROP_FRAME_HEIGHT, 720) #1944

print(vid.get(cv.CAP_PROP_FRAME_WIDTH), vid.get(cv.CAP_PROP_FRAME_HEIGHT))

framenum = 0
scale_factor = 1

fourcc = cv.VideoWriter_fourcc(*'XVID')
# fourcc = cv.VideoWriter_fourcc(*'H264')
vid_out1 = None
vid_out2 = None
tEnd = time.time()

track_x = []
track_y = []

while vid.isOpened():
    
    framenum +=1

    ret, img1 = vid.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

    # detect stars
    t0 = time.time()

    # -- Method 1: use moments ie. find centroid -- 
    moments = cv.moments(gray1)
    x = moments["m10"]/moments["m00"]
    y = moments["m01"]/moments["m00"]
    print(f"{x:.3f}\t{y:.3f}")

    # display
    out_img = img1
    cv.circle(out_img, tuple((round(x), round(y))) , 0, (0, 255, 0), thickness=-1)
    cv.circle(out_img, tuple((round(x), round(y))) , 10, (0, 255, 0), thickness=1)
    out_img_disp = cv.resize(out_img, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
    # match_img_disp = cv.resize(match_img, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
    cv.putText(out_img_disp,"{:.2f} fps".format(1/(t0-tEnd)),(10,25),cv.FONT_HERSHEY_COMPLEX,0.5,(25,255,255),1)
    # cv.putText(match_img_disp,"{:.2f} fps".format(1/(t0-tEnd)),(10,25),cv.FONT_HERSHEY_COMPLEX,0.5,(25,255,255),1)
    cv.imshow("tracking", out_img_disp)
    # cv.imshow("matches", match_img_disp)
    
    track_x.append(x)
    track_y.append(y)

    if RECORD_VIDEO:
        if vid_out1 is None:
            w, h = out_img.shape[:2]
            vid_out1 = cv.VideoWriter(os.path.join(media_path, f"{ref}-track-centroid.avi"), fourcc, 20.0, (h, w))
            print(vid_out1.isOpened(), out_img.shape[:2])

        # if vid_out2 is None:
        #     w, h = match_img.shape[:2]
        #     vid_out2 = cv.VideoWriter(os.path.join(media_path, f"{ref}-matches.avi"), fourcc, 20.0, (h, w))
        #     print(vid_out2.isOpened(), match_img.shape[:2])

        vid_out1.write(out_img)
        # vid_out2.write(match_img)

    k = cv.waitKey(delay=1)
    if k == 'q':
        break

    if framenum % 60 == 0:
        print("FPS = {:.2f}".format(1/(t0-tEnd)))
        # break

    tEnd = t0
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
    vid_out2.release()
except:
    pass

# plot results
fig1, axes = plt.subplots(1,2)
plt.subplots_adjust(0.05,0.1,0.95,0.9)
axes[0].set_title("y position - centroid")
axes[0].set_xlabel("frame number")
axes[0].plot(track_x)
axes[1].set_title("y position - centroid")
axes[1].set_xlabel("frame number")
axes[1].plot(track_y)

plt.show()

# k = cv.waitKey(0)
# if k == ord("c"):
#     pass