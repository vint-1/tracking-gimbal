from turtle import back
import cv2 as cv
from cv2 import COLOR_BGR2RGB
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# from picamera.array import PiRGBArray
# from picamera import PiCamera

# camera=PiCamera(sensor_mode=2)
# camera.resolution=(2592,1944)
# camera.exposure_compensation=-6
# camera.meter_mode='backlit'
# camera.framerate=60

ref_ext = "jpg"
ref = "stars-capture"
out_dir = "tracking"
vid_num = 0
algo_name = "gaussian-symm-fit"

ext = "png"

RECORD_VIDEO = False

script_path = os.path.dirname(os.path.realpath(__file__))
proj_path = os.path.dirname(script_path)
media_path = os.path.join(proj_path, "media", "stars", "first-light")

vid = cv.VideoCapture(os.path.join(media_path, f"{ref}-{vid_num}.avi"))

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

def plot_img_surface(img, ax = None, is_show = False, title = ""):
    if ax is None:
        _, ax = plt.subplots(subplot_kw={"projection": "3d"})
        plt.subplots_adjust(0.05,0.1,0.95,0.9)
    X = np.arange(0, img.shape[0])
    Y = np.arange(0, img.shape[1])
    X, Y = np.meshgrid(X, Y, indexing = 'ij')
    ax.plot_surface(X, Y, img, cmap="coolwarm")
    ax.set_title(title)
    if is_show:
        plt.show()

def plot_img(img, ax = None, is_show = False, title = "", **kwargs):
    if ax is None:
        _, ax = plt.subplots()
        plt.subplots_adjust(0.05,0.1,0.95,0.9)
    plt.colorbar(ax.imshow(img, cmap="plasma", **kwargs), ax = ax)
    ax.set_title(title)
    if is_show:
        plt.show()

def roi(image, center, radius):
    """ Crops a region of interest in image centered around specified point. If center is too close to the boundaries, then return whatever is within bounds of image
        Returns the RoI image, and global coordinates of top left pixel
    """
    image_width = image.shape[1]
    image_height = image.shape[0]
    bounds = (np.minimum(radius, center[0]), np.minimum(radius, image_width-center[0]-1), np.minimum(radius, center[1]), np.minimum(radius, image_height-center[1]-1),) # left, right, top, bottom
    return image[center[1]-bounds[2]:center[1]+bounds[3]+1, center[0]-bounds[0]:center[0]+bounds[1]+1], center[0]-bounds[0], center[1]-bounds[2]

def centroid(image):
    moments = cv.moments(image)
    x = moments["m10"]/moments["m00"]
    y = moments["m01"]/moments["m00"]
    return x, y

def adv_centroid(image):
    scale = 200
    final_scale = 25
    moments = cv.moments(image)
    x_ct = moments["m10"]/moments["m00"]
    y_ct = moments["m01"]/moments["m00"]
    x_offset_global = 0
    y_offset_global = 0
    while scale > final_scale:
        scale = round(scale/2)
        image, x_offset, y_offset = roi(image, (round(x_ct), round(y_ct)), scale)
        x_offset_global += x_offset
        y_offset_global += y_offset
        moments = cv.moments(image)
        x_ct = moments["m10"]/moments["m00"]
        y_ct = moments["m01"]/moments["m00"]
    return x_offset_global + x_ct, y_offset_global + y_ct

def star_extract(image):
    # plot_img_surface(image, is_show=False, title = "original image")

    bg_iterations = 2
    n = 4
    max_stars = 1

    mask = np.zeros_like(image)
    for i in range(bg_iterations):
        masked_img = np.ma.array(image, mask = mask)
        # median = np.ma.median(masked_img)
        mean = np.ma.mean(masked_img)
        sigma = np.ma.std(masked_img)
        mask = image > mean + n * sigma
        # plot_img(mask, is_show=False, title = f"{i}")
    
    blurred = cv.GaussianBlur(image, (9, 9), 2)
    mask = blurred > mean + n * sigma
    background = mean

    n_cc, _, stats, centroids = cv.connectedComponentsWithStats(mask.astype(np.uint8), ltype = cv.CV_16U)

    stars = []
    
    labels = [i for i in range(1, n_cc)]
    labels.sort(key = lambda x:stats[x, cv.CC_STAT_AREA])

    conn_components = []
    for comp_num in range(1, n_cc):
        # preprocess images to find most promising connected components
        if stats[comp_num, cv.CC_STAT_AREA] < 16:
            # not enough points to fit
            continue

        bounds = (stats[comp_num, cv.CC_STAT_TOP], stats[comp_num, cv.CC_STAT_TOP] + stats[comp_num, cv.CC_STAT_HEIGHT], stats[comp_num, cv.CC_STAT_LEFT], stats[comp_num, cv.CC_STAT_LEFT] + stats[comp_num, cv.CC_STAT_WIDTH]) # top, bottom, left, right
        comp_roi = image[bounds[0]:bounds[1], bounds[2]:bounds[3]]
        conn_components.append((np.sum(comp_roi), comp_num))
    
    conn_components.sort(reverse=True)
    if len(conn_components) > 10:
        print(len(conn_components))

    for comp_amp, comp_num in conn_components[:max_stars]:

        bounds = (stats[comp_num, cv.CC_STAT_TOP], stats[comp_num, cv.CC_STAT_TOP] + stats[comp_num, cv.CC_STAT_HEIGHT], stats[comp_num, cv.CC_STAT_LEFT], stats[comp_num, cv.CC_STAT_LEFT] + stats[comp_num, cv.CC_STAT_WIDTH]) # top, bottom, left, right
        comp_mask = mask[bounds[0]:bounds[1], bounds[2]:bounds[3]]
        comp_roi = image[bounds[0]:bounds[1], bounds[2]:bounds[3]]
        comp_img = comp_mask * (comp_roi - background)

        # compute x and y positions using centroids
        # moments = cv.moments(comp_mask * (comp_roi - background))
        # comp_x = stats[comp_num, cv.CC_STAT_LEFT] + moments["m10"]/moments["m00"]
        # comp_y = stats[comp_num, cv.CC_STAT_TOP] + moments["m01"]/moments["m00"]
        # stars.append((moments["m00"], comp_x, comp_y))

        # compute x and y positions using gaussian fit
        
        try:
            comp_x, comp_y = gaussian_fit(comp_img, x_guess = centroids[comp_num, 0]-stats[comp_num, cv.CC_STAT_LEFT], y_guess = centroids[comp_num, 1]-stats[comp_num, cv.CC_STAT_TOP], symm = True)
            comp_x = stats[comp_num, cv.CC_STAT_LEFT] + comp_x
            comp_y = stats[comp_num, cv.CC_STAT_TOP] + comp_y
            stars.append((comp_amp, comp_x, comp_y))
        except:
            pass     

    stars.sort(reverse=True) # sort in decreasing order of total brightness 
    # print(stars)
    # x, y = centroid(mask * (blurred-background))
    # fig, axes = plt.subplots(1,2)
    # plt.subplots_adjust(0.05,0.1,0.95,0.9)
    # plot_img(image, is_show=False, ax = axes[0])
    # plot_img(labels, ax = axes[1])
    # plt.show()
    return stars[0][1:]

def gaussian_fn(x, ctr_x, ctr_y, k_x, k_y, k_xy, mag):
    r = x - np.array([[ctr_x], [ctr_y]])
    sig = np.array([[k_x, k_xy],[k_xy, k_y]])
    return mag * np.exp( - np.einsum("ij,ij -> j",r, (sig @ r)))

def sym_gaussian_fn(x, ctr_x, ctr_y, k, mag):
    r = x - np.array([[ctr_x], [ctr_y]])
    return mag * np.exp( - k * np.einsum("ij,ij -> j",r, r))

def gaussian_fit(image, x_guess = 1, y_guess = 1, symm = False):
    X = np.arange(0, image.shape[0])
    Y = np.arange(0, image.shape[1])
    Y, X = np.meshgrid(X, Y, indexing = 'ij')
    xy = np.stack((X,Y), axis=0).reshape((2, -1))
    z = image.reshape((-1))
    if not symm:
        # do full gaussian fit
        opt, _ = curve_fit(gaussian_fn, xy, z, p0 = (x_guess, y_guess, 0.3, 0.3, 0, 100))
    else:
        opt, _ = curve_fit(sym_gaussian_fn, xy, z, p0 = (x_guess, y_guess, 0.3, 100))
    # plot_img(gaussian_fn(xy, 15, 10, .3, .3, 0, 10).reshape(image.shape[0],image.shape[1]))
    return opt[0], opt[1]

lastPrint = time.time()

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
    # x, y = centroid(gray1)

    # -- Method 2: use centroids, but iteratively --
    # try:
    #     x, y = adv_centroid(gray1)
    # except ZeroDivisionError as e:
    #     print("could not find star")
    #     x = 0
    #     y = 0
    
    # print(f"{x:.3f}\t{y:.3f}\t{roi_x:.3f}\t{roi_y:.3f}")

    # -- Method 3: use star-extract
    # gray2, offset_x, offset_y = roi(gray1, (round(x),round(y)), 50)
    x, y = star_extract(gray1)
    # x += offset_x
    # y += offset_y
    roi_1, roi_x, roi_y = roi(img1, (round(x),round(y)), 20)

    # display
    out_img = img1
    cv.circle(out_img, tuple((round(x), round(y))) , 0, (0, 255, 0), thickness=-1)
    cv.circle(out_img, tuple((round(x), round(y))) , 10, (0, 255, 0), thickness=1)
    out_img_disp = cv.resize(out_img, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
    roi_disp = cv.resize(roi_1, None, fx=8, fy=8, interpolation=cv.INTER_AREA)
    cv.putText(out_img_disp,"{:.2f} fps".format(1/(t0-tEnd)),(10,25),cv.FONT_HERSHEY_COMPLEX,0.5,(25,255,255),1)
    # cv.putText(match_img_disp,"{:.2f} fps".format(1/(t0-tEnd)),(10,25),cv.FONT_HERSHEY_COMPLEX,0.5,(25,255,255),1)
    cv.imshow("tracking", out_img_disp)
    cv.imshow("RoI", roi_disp)

    # plot, for diagnostics
    # if framenum % 120 == 0:
    #     img, _, _ = roi(gray1, (round(x),round(y)), 25)
    #     plot_img_surface(img, is_show=True)

    track_x.append(x)
    track_y.append(y)

    if RECORD_VIDEO:
        if vid_out1 is None:
            w, h = out_img.shape[:2]
            vid_out1 = cv.VideoWriter(os.path.join(media_path, out_dir, f"{ref}-track-{algo_name}-{vid_num}.avi"), fourcc, 20.0, (h, w))
            print(vid_out1.isOpened(), out_img.shape[:2])

        if vid_out2 is None:
            w, h = roi_disp.shape[:2]
            vid_out2 = cv.VideoWriter(os.path.join(media_path, out_dir, f"{ref}-roi-{algo_name}-{vid_num}.avi"), fourcc, 20.0, (h, w))
            print(vid_out2.isOpened(), roi_disp.shape[:2])

        vid_out1.write(out_img)
        vid_out2.write(roi_disp)

    k = cv.waitKey(delay=1)
    if k == 'q':
        break

    if framenum % 60 == 0:
        print("FPS = {:.2f}".format(60/(time.time() - lastPrint)))
        lastPrint = time.time()
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
axes[0].set_title(f"x position - {algo_name}")
axes[0].set_xlabel("frame number")
axes[0].plot(track_x)
axes[1].set_title(f"y position - {algo_name}")
axes[1].set_xlabel("frame number")
axes[1].plot(track_y)

plt.show()

# k = cv.waitKey(0)
# if k == ord("c"):
#     pass