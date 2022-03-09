import cv2 as cv
from cv2 import COLOR_BGR2RGB
import os
import time
import numpy as np
import pathutils
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from datetime import datetime

offline_test = True
debug_timing = False

def main(PROCESS_IMG, LIVE_DISPLAY, RECORD_VIDEO, OBJ_COORD):

    ref = "lad4"
    mode = "rockets"
    out_dir = "tracking"
    algo_name = "goturn"
    vid_num = 2

    if offline_test:
        vid = cv.VideoCapture(os.path.join(pathutils.media_path, f"{mode}", f"{ref}-{vid_num}.mp4"))
        print(os.path.join(pathutils.media_path, f"{ref}-{vid_num}.mp4"))

    else:
        vid = cv.VideoCapture(0, cv.CAP_V4L2)
        vid.set(cv.CAP_PROP_FRAME_WIDTH, 960) #2592
        vid.set(cv.CAP_PROP_FRAME_HEIGHT, 720) #1944

    print(vid.get(cv.CAP_PROP_FRAME_WIDTH), vid.get(cv.CAP_PROP_FRAME_HEIGHT))

    framenum = 0
    scale_factor = 4

    fourcc = cv.VideoWriter_fourcc(*'XVID')
    # fourcc = cv.VideoWriter_fourcc(*'H264')
    vid_out1 = None
    tEnd = time.time()

    track_x = []
    track_y = []

    lastPrint = time.time()

    tracker = cv.TrackerGOTURN_create()

    while vid.isOpened():

        process_img_flag = PROCESS_IMG
        live_display_flag = LIVE_DISPLAY
        record_video_flag = RECORD_VIDEO
        
        t0 = time.time()

        framenum +=1

        ret, img1 = vid.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        gray1 = cv.cvtColor(img1, cv.COLOR_BGR2GRAY)

        # detect rocket
        t1 = time.time()
        
        x,y = 10,10
        if framenum == 1:
            # get first bounding box
            resized_img = cv.resize(img1, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
            box = cv.selectROI(resized_img, False)
            box = tuple([round(coord * scale_factor) for coord in box])
            print(box)
            # cv.destroyAllWindows()
            is_detect = tracker.init(img1, box)
        else:
            is_detect, box = tracker.update(img1)

        x = box[0] + box[2]//2 if is_detect else -1
        y = box[1] + box[3]//2 if is_detect else -1
        track_x.append(x)
        track_y.append(y)

        t2 = time.time()

        # display
        if live_display_flag or record_video_flag:
            
            out_img = img1

            if (x,y) != (-1,-1):
                # cv.circle(out_img, tuple((round(x), round(y))) , 0, (0, 255, 0), thickness=-1)
                # cv.circle(out_img, tuple((round(x), round(y))) , 10, (0, 255, 0), thickness=1)
                # roi_1, roi_x, roi_y = roi(img1, (round(x),round(y)), 20)
                # roi_disp = cv.resize(roi_1, None, fx=8, fy=8, interpolation=cv.INTER_AREA)
                cv.rectangle(out_img,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(20,20,255),4)
            else:
                roi_disp = None

            out_img_disp = cv.resize(out_img, None, fx=1/scale_factor, fy=1/scale_factor, interpolation=cv.INTER_AREA)
            cv.putText(out_img_disp,"{:.2f} fps".format(1/(t0-tEnd)),(10,25),cv.FONT_HERSHEY_COMPLEX,0.5,(25,255,255),1)

        if live_display_flag:
            cv.imshow("tracking", out_img_disp)
            # if roi_disp is not None:
                # cv.imshow("RoI", roi_disp)
        else:
            cv.destroyAllWindows()
        t3 = time.time()

        # plot, for diagnostics
        # if framenum % 120 == 0:
        #     img, _, _ = roi(gray1, (round(x),round(y)), 25)
        #     plot_img_surface(img, is_show=True)

        if record_video_flag:
            if vid_out1 is None:
                w, h = out_img.shape[:2]
                if offline_test:
                    vid_out1 = cv.VideoWriter(os.path.join(pathutils.media_path, out_dir, f"{ref}-track-{algo_name}-{vid_num}.avi"), fourcc, 20.0, (h, w))
                else:
                    timestamp = datetime.now().strftime("%y-%m-%d")
                    vid_out1 = cv.VideoWriter(os.path.join(pathutils.media_path, out_dir, f"{timestamp}-{ref}-track-{algo_name}.avi"), fourcc, 20.0, (h, w))
                print(vid_out1.isOpened(), out_img.shape[:2])

            # if vid_out2 is None:
            #     w, h = roi_disp.shape[:2]
            #     vid_out2 = cv.VideoWriter(os.path.join(media_path, out_dir, f"{ref}-roi-{algo_name}-{vid_num}.avi"), fourcc, 20.0, (h, w))
            #     print(vid_out2.isOpened(), roi_disp.shape[:2])

            vid_out1.write(out_img)
            # if roi_disp is not None:
            #     vid_out2.write(roi_disp)

        t4 = time.time()

        k = cv.waitKey(delay=1)
        if k == ord('q'):
            break

        if framenum % 60 == 0:
            print("FPS = {:.2f}\t x = {:.2f} \t y = {:.2f}".format(60/(time.time() - lastPrint), x, y))
            lastPrint = time.time()
            # break

        if debug_timing:
            print(f"({x:.2f}\t{y:.2f})\t Reading: {t1-t0:.3f}s\t Star Extraction: {t2-t1:.3f}s\t Display: {t3-t2:.3f}s\t Recording: {t4-t3:.3f}s")

        t5 = time.time()
        tEnd = t0

    try:
        vid.release()
        vid_out1.release()
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


if __name__ == "__main__":
    main(True, True, False, False)