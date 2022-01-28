import cv2 as cv
from cv2 import COLOR_BGR2RGB
import matplotlib.pyplot as plt
import os
import time

ref_ext = "jpg"
ref = "campanile-day"

ext = "png"

script_path = os.path.dirname(os.path.realpath(__file__))
proj_path = os.path.dirname(script_path)
media_path = os.path.join(proj_path, "media")

reference_img = cv.imread(os.path.join(media_path, f"{ref}.{ref_ext}"))
img1 = cv.imread(os.path.join(media_path, f"{ref}-3.{ext}"))
gray = cv.cvtColor(reference_img, cv.COLOR_BGR2GRAY)
gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

fast = cv.FastFeatureDetector_create()

# detect SIFT keypoints
t0 = time.time()
kp = fast.detect(gray, None)
kp1 = fast.detect(gray1, None)
t1 = time.time()

cv.drawKeypoints(reference_img, kp, reference_img, flags = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

brief = cv.xfeatures2d.BriefDescriptorExtractor_create()
_, des  = brief.compute(gray, kp)

print(des.shape)
print(des)

print("FAST detected in {:.3f}s".format(t1-t0))
fig1, axes = plt.subplots(1,1)
plt.subplots_adjust(0.02,0.1,0.98,0.9)
# axes.imshow(cv.cvtColor(reference_img, cv.COLOR_BGR2RGB))
axes.imshow(cv.cvtColor(reference_img,cv.COLOR_BGR2RGB))
axes.axis('off')
plt.show()

k = cv.waitKey(0)
if k == ord("c"):
    pass