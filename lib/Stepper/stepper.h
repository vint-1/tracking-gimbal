#pragma once
#include <Arduino.h>

#define MODE_POS_CTRL 1
#define MODE_SPD_CTRL 2

// #define MAX_SPEED 1000 // microsteps/sec
#define MAX_SPEED 6400e-6
#define MAX_ACCEL 10000 // microsteps/sec^2
#define PULSE_TIME 50 // in us
#define UPDATE_PERIOD 1000 //in us

/*
Created by Vint Lee 2022
*/

namespace Stepper{

    class Stepper{
        
        unsigned step_pin;
        unsigned dir_pin;
        int pulse_time;
        int mode = MODE_POS_CTRL;
        
        // for position control
        long pos_setpoint = 0;
        long stepcount = 0;
        uint64_t last_step = 0;

        // for tracking individual steps in non-blocking manner
        bool is_step = false;
        bool is_forward = true; // +/- 1
        bool is_step_high = false;

        // for velocity control
        uint64_t last_spd_chg = 0;
        double pos_last_spd_chg = 0;
        double spd_setpoint = 0;
        double current_spd = 0;
        double fine_pos_setpoint = 0;

        public:
        Stepper(unsigned step_pin, unsigned dir_pin, int pulse_time);

        void step(); //blocking
        void set_pos_target(long set_pos); //pos is in steps
        void set_spd_target(double set_spd); //speed is in steps/s
        void update(); //non-blocking

        long get_stepcount();
        long get_pos_setpoint();
        double get_speed();

    };

}