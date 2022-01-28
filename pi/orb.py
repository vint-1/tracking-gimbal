import cv2 as cv
from cv2 import COLOR_BGR2RGB
import matplotlib.pyplot as plt
import os
import time
import numpy as np

ref_ext = "jpg"
ref = "campanile-day"

ext = "png"

script_path = os.path.dirname(os.path.realpath(__file__))
proj_path = os.path.dirname(script_path)
media_path = os.path.join(proj_path, "media")

ref_img = cv.imread(os.path.join(media_path, f"{ref}-crop.{ref_ext}"))
# img1 = cv.imread(os.path.join(media_path, f"{ref}-2.{ext}"))
gray = cv.cvtColor(ref_img, cv.COLOR_BGR2GRAY)

orb = cv.ORB_create(nfeatures = 500)
bf = cv.BFMatcher(cv.NORM_L2, crossCheck = True)

ref_kp, ref_desc = orb.detectAndCompute(gray, None)

vid = cv.VideoCapture(os.path.join(media_path, f"{ref}-1.h264"))
framenum = 0
scale_factor = 4

fourcc = cv.VideoWriter_fourcc(*'DIVX')
vid_out1 = None
vid_out2 = None

while vid.isOpened():
    
    framenum +=1

    ret, img1 = vid.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)
    if vid_out1 is None:
        vid_out1 = cv.VideoWriter(os.path.join(media_path, f"{ref}-track.avi"), fourcc, 20.0, gray1.shape)
        print(vid_out1.isOpened())

    if vid_out2 is None:
        vid_out2 = cv.VideoWriter(os.path.join(media_path, f"{ref}-matches.avi"), fourcc, 20.0, gray1.shape)
        print(vid_out1.isOpened())

    # detect SIFT keypoints
    t0 = time.time()
    kp1, desc1 = orb.detectAndCompute(gray1, None)
    t1 = time.time()

    # cv.drawKeypoints(reference_img, kp, reference_img, flags = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # match keypoints
    if len(kp1) > 0:
        matches = bf.match(ref_desc, desc1)
    else:
        # cv.imshow("debug",cv.resize(cv.drawKeypoints(img1, kp1, img1, flags = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS), None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA))
        # print(kp1)
        # print(desc1)
        # cv.waitKey(0)
        matches = []
        
    t2 = time.time()

    n=32 # display n best matches
    thresh = 8
    matches = sorted(matches, key = lambda x: x.distance)
    match_img = cv.drawMatches(ref_img, ref_kp, img1, kp1, matches[:n], None, flags = cv.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS + cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # match_img = cv.drawMatches(ref_img, ref_kp, img1, kp1, matches[:n], None, flags = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    src_pts = np.float32([ ref_kp[m.queryIdx].pt for m in matches]).reshape(-1,1,2)
    dst_pts = np.float32([ kp1[m.trainIdx].pt for m in matches]).reshape(-1,1,2)
    t3 = time.time()

    if len(matches) >= thresh:

        # find homography
        tf, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, ransacReprojThreshold=10)
        t4 = time.time()

        # drawing bounding box
        h, w = gray.shape
        pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv.perspectiveTransform(pts,tf)
        out_img = cv.polylines(img1,[np.int32(dst)],True,(50, 255, 255),2, cv.LINE_4)

        # drawing keypoints
        dst_kp = cv.perspectiveTransform(src_pts,tf)
        for i in range(dst_kp.shape[0]):
            color = (0, 255, 0) if mask[i, 0] else (0, 0, 255)
            cv.circle(out_img, np.int32(dst_kp[i, 0, :]) , 4, color, thickness = -1)

    else:
        # print("failed to detect")
        out_img = img1
        t4 = time.time()

    
    out_img_disp = cv.resize(out_img, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
    match_img_disp = cv.resize(match_img, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
    cv.imshow("tracking", out_img_disp)
    cv.imshow("matches", match_img_disp)
    
    vid_out1.write(out_img_disp)
    vid_out2.write(match_img_disp)

    cv.waitKey(delay=1)

    if framenum % 60 == 0:
        print("ORB detected and computed in {:.3f}s".format(t1-t0), "\t Matching in {:.3f}s".format(t2-t1), "\t Homography in {:.3f}s".format(t4-t3))

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

k = cv.waitKey(0)
if k == ord("c"):
    pass