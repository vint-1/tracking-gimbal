#include <stepper.h>

namespace Stepper{

    Stepper::Stepper(unsigned step_pin, unsigned dir_pin, int pulse_time) {
        this->step_pin = step_pin;
        this->dir_pin = dir_pin;
        this->pulse_time = pulse_time;
    }

    void Stepper::step() {
        digitalWrite(this->step_pin, HIGH);
        delayMicroseconds(pulse_time);
        digitalWrite(this->step_pin, LOW);
        delayMicroseconds(pulse_time);
    }

    void Stepper::set_pos_target(long set_pos){
        
    }

}