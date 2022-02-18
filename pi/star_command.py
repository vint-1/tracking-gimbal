import ctypes
import star_detect
import comms
import multiprocessing as mp
import multiprocessing.sharedctypes as mpc
import telemetry

# defaults
# acq_proc_img = True
acq_proc_img = False
trk_record_vid = False
record_telemetry = True


def main(PROCESS_IMG, LIVE_DISPLAY, RECORD_VIDEO, OBJ_COORD):
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
    is_telemetry = False
    telemetry_writer = telemetry.csvWriter(header = ["time", "obj_x", "obj_y", "setspd_x", "setspd_y", "spd_x", "spd_y", "step_x", "step_y"])

    def switch_to_mode(new_mode):

        nonlocal mode
        nonlocal is_telemetry
        nonlocal telemetry_writer

        if new_mode == "trk":
            print("--- Switching to tracking mode ---")
            PROCESS_IMG.value = True
            LIVE_DISPLAY.value = False
            RECORD_VIDEO.value = trk_record_vid

            if mode == "trk": # already in tracking mode, nothing to do
                return
        
            # initialize telemetry
            telemetry_writer.open()
            mode = "trk"
            is_telemetry = True

        elif new_mode == "acq":
            print("--- Switching to acquisition mode ---")
            PROCESS_IMG.value = acq_proc_img
            LIVE_DISPLAY.value = True
            RECORD_VIDEO.value = False

            if mode == "acq": # already in acquition mode, nothing to do
                return
            
            # close telemetry
            telemetry_writer.close()
            mode = "acq"
            is_telemetry = False

        else:
            print(f"--- Unknown mode: {new_mode} ---")

    switch_to_mode("acq")

    last_update = 0

    while True:
        # write new data if available
        update_time, obj_x, obj_y = OBJ_COORD[:]
        if mode == "trk" and update_time != last_update:
            comms.write_coord(obj_x, obj_y)
            last_update = update_time

        # read telemetry / commands if available
        line = comms.read()
        if line is not None:
            split = line.split(",")
            if len(split) == 1: # command detected
                switch_to_mode(split[0])
                continue
            elif is_telemetry and record_telemetry: # telemetry data incoming, record it
                telemetry_writer.write(split)

if __name__ == "__main__":

    PROCESS_IMG = mpc.RawValue(ctypes.c_bool, False) # no lock because only star_command will write 
    LIVE_DISPLAY = mpc.RawValue(ctypes.c_bool, False) # no lock because only star_command will write
    RECORD_VIDEO = mpc.RawValue(ctypes.c_bool, False) # no lock because only star_command will write 
    OBJ_COORD = mp.Array("d", 3, lock = True) # first entry is write_time, 2nd is x, 3rd is y

    p = mp.Process(target = star_detect.main, args = (PROCESS_IMG, LIVE_DISPLAY, RECORD_VIDEO, OBJ_COORD))
    p.start()
    main(PROCESS_IMG, LIVE_DISPLAY, RECORD_VIDEO, OBJ_COORD)
    # p.join()
