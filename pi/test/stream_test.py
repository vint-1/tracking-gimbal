import cv2 as cv
from cv2 import COLOR_BGR2RGB
import os
import time
from cv2 import CAP_GSTREAMER
import numpy as np
import pathutils
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime


offline_test = False
debug_timing = False

def main():

    vid = cv.VideoCapture("-v v4l2src device=/dev/video0 num-buffers=-1 ! video/x-raw,width=1280,height=720, framerate=30/1 ! appsink", cv.CAP_GSTREAMER)
    # vid = cv.VideoCapture(0, cv.CAP_V4L2)
    # vid.set(cv.CAP_PROP_FRAME_WIDTH, 960) #2592
    # vid.set(cv.CAP_PROP_FRAME_HEIGHT, 720) #1944

    print(vid.get(cv.CAP_PROP_FRAME_WIDTH), vid.get(cv.CAP_PROP_FRAME_HEIGHT))

    framenum = 0

    fourcc = cv.VideoWriter_fourcc(*'XVID')
    # fourcc = cv.VideoWriter_fourcc(*'H264')
    vid_view = None


    lastPrint = time.time()

    while vid.isOpened():

        framenum +=1

        ret, img1 = vid.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        
        out_img = img1
        if vid_view is None:
            h, w = out_img.shape[:2]
            # vid_view = cv.VideoWriter("appsrc ! videoconvert ! jpegenc ! jpegdec ! autovideosink", cv.CAP_GSTREAMER, 30.0, (w, h))
            vid_view = cv.VideoWriter("appsrc ! videoconvert ! jpegenc ! multipartmux ! tcpserversink  host=10.0.0.153 port=5000", cv.CAP_GSTREAMER, 30.0, (w, h))
            print(vid_view.isOpened(), h, w)
        vid_view.write(out_img)

        if framenum % 60 == 0:
            print("FPS = {:.2f}\t x = {:.2f} \t y = {:.2f}".format(60/(time.time() - lastPrint), 0, 0))
            lastPrint = time.time()
            # break


    try:
        vid.release()
        vid_view.release()
    except:
        pass

if __name__ == "__main__":
    main()

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

def star_extract(image, is_profile = False):

    n = 10
    max_stars = 5

    t0 = time.time()

    # identify background statistics - ideally, we'd do multiple iterations, and use stddev so stars aren't included
    mean = np.mean(image)
    med = np.median(image)
    # c = (image - mean).reshape((-1))
    # sigma = np.sqrt(np.dot(c,c)/c.shape[0])
    
    blurred = cv.GaussianBlur(image, (7, 7), 2)
    mask = blurred > (mean + max(n * (mean - med), 1))
    t1 = time.time()
    background = mean

    n_cc, _, stats, centroids = cv.connectedComponentsWithStats(mask.astype(np.uint8), ltype = cv.CV_16U)
    
    stars = []
    
    t2 = time.time()
    conn_components = []
    for comp_num in range(1, n_cc):
        # preprocess images to find most promising connected components
        if stats[comp_num, cv.CC_STAT_AREA] < 10:
            # not enough points to fit
            continue

        bounds = (stats[comp_num, cv.CC_STAT_TOP], stats[comp_num, cv.CC_STAT_TOP] + stats[comp_num, cv.CC_STAT_HEIGHT], stats[comp_num, cv.CC_STAT_LEFT], stats[comp_num, cv.CC_STAT_LEFT] + stats[comp_num, cv.CC_STAT_WIDTH]) # top, bottom, left, right
        comp_roi = image[bounds[0]:bounds[1], bounds[2]:bounds[3]]
        conn_components.append((np.sum(comp_roi), comp_num))
    
    conn_components.sort(reverse=True)

    t3 = time.time()

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
    # plot_img(mask, ax = axes[1])
    # plt.show()

    t4 = time.time()

    if is_profile:
        print(f"{n_cc}\t Background id: {t1-t0:.3f}s\t CC: {t2-t1:.3f}s\t Preproc: {t3-t2:.3f}s\t Fitting: {t4-t3:.3f}s")

    return stars[0][1:] if len(stars)>0 else None

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
