#pragma once
#include <Arduino.h>
#define PI_SERIAL Serial7
#define BAUD_RATE 115200
#define TELEMETRY_DP 4

// TODO: Use char buffers instead of String class to improve memory performance 

namespace Comms {
    int parse(float *output);
    int writeln(String input);
    int write_telemetry(uint32_t time,
                        float * obj_pos,
                        double target_spd_x, double target_spd_y,
                        double curr_spd_x, double curr_spd_y,
                        long stepcount_x, long stepcount_y,
                        double x_int, double y_int);
    // Telemetry format:
    // time (us); obj x,y (px); spd target x,y (uS/s); spd current x,y (uS/s); microsteps x,y; integral x,y;

}