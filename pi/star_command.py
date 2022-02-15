import ctypes
import star_detect
import comms
import multiprocessing as mp
import multiprocessing.sharedctypes as mpc

# defaults
acq_proc_img = True
trk_record_vid = False
record_telemetry = True


def main(PROCESS_IMG, LIVE_DISPLAY, RECORD_VIDEO):
    """
    Control logic for commanding star tracker system
    Starts in acquisition mode
        - Image processing: OPT
        - Video display:    YES
        - Video record:     NO
        - Telemetry:        NO
    Switch to tracking mode based on teensy signal
        - Image processing: YES
        - Video display:    NO
        - Video record:     OPT
        - Telemetry:        YES
    """
    mode = "acq"
    telemetry = False

    def switch_to_mode(new_mode):

        nonlocal mode
        nonlocal telemetry

        if new_mode == "trk":
            print("--- Switching to tracking mode ---")
            PROCESS_IMG.value = True
            LIVE_DISPLAY.value = False
            RECORD_VIDEO.value = trk_record_vid

            if mode == "trk": # already in tracking mode, nothing to do
                return
        
            # initialize telemetry

            mode = "trk"
            telemetry = True

        elif new_mode == "acq":
            print("--- Switching to acquisition mode ---")
            PROCESS_IMG.value = acq_proc_img
            LIVE_DISPLAY.value = True
            RECORD_VIDEO.value = False

            if mode == "acq": # already in acquition mode, nothing to do
                return
            
            # close telemetry

            mode = "acq"
            telemetry = False

        else:
            print(f"--- Unknown mode: {new_mode} ---")

    switch_to_mode("acq")

    while True:
        line = comms.read()
        if line is not None:
            split = line.split(",")
            if len(split) == 1: # command detected
                switch_to_mode(split[0])
                continue
            elif telemetry and record_telemetry: # telemetry data incoming, record it
                print("hi")
                # print(split)
            

if __name__ == "__main__":

    PROCESS_IMG = mpc.RawValue(ctypes.c_bool, False) # no lock because only star_command will write 
    LIVE_DISPLAY = mpc.RawValue(ctypes.c_bool, False) # no lock because only star_command will write
    RECORD_VIDEO = mpc.RawValue(ctypes.c_bool, False) # no lock because only star_command will write 
    
    p = mp.Process(target = star_detect.main, args = (PROCESS_IMG, LIVE_DISPLAY, RECORD_VIDEO))
    p.start()
    main(PROCESS_IMG, LIVE_DISPLAY, RECORD_VIDEO)
    # p.join()
