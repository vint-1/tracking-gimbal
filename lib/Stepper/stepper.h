#pragma once
#include <Arduino.h>

namespace Stepper{
    class Stepper{
        
        unsigned step_pin;
        unsigned dir_pin;
        int pulse_time;
        int mode;
        
        long pos_setpoint = 0;
        long stepcount = 0;
        uint64_t lastStep = 0;

        Stepper(unsigned step_pin, unsigned dir_pin, int pulse_time);

        void Stepper::step(); //blocking
        void Stepper::set_pos_target(long set_pos); //pos is in steps
        void Stepper::set_spd_target(double set_spd); //speed is in steps/s
        void Stepper::update(); //non-blocking

    };

}