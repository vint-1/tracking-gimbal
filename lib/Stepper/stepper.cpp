#include <stepper.h>

/*
Created by Vint Lee 2022
*/

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
        this->mode = MODE_POS_CTRL;
        this->pos_setpoint = set_pos;
    }

    void Stepper::set_spd_target(double set_spd){
        set_spd = max(-MAX_SPEED, min(MAX_SPEED, set_spd)) * 1e-6; // convert units to microsteps/us
        // The timing here is crucial
        uint64_t new_spd_chg = micros();
        if (this->mode == MODE_SPD_CTRL) {
            this->fine_pos_setpoint = this->pos_last_spd_chg + (this->current_spd * (new_spd_chg - this->last_spd_chg));
            // update acceleration
            double spd_delta = MAX_ACCEL * ((new_spd_chg - this->last_accel_update) / 1.0e6) / 1.0e6; // convert units to microsteps/us^2
            this->current_spd = max(this->current_spd - spd_delta,min(this->current_spd + spd_delta, this->spd_setpoint)); 
        }
        
        this->mode = MODE_SPD_CTRL;
        this->spd_setpoint = set_spd;
        this->last_accel_update = new_spd_chg;
        this->last_spd_chg = new_spd_chg;
        this->pos_last_spd_chg = this->fine_pos_setpoint;
    }

    void Stepper::update(){
        
        if (this->mode == MODE_SPD_CTRL) {
            
            uint32_t timenow = micros();
            // update acceleration
            double spd_delta = MAX_ACCEL * ((timenow - this->last_accel_update) / 1.0e6) / 1.0e6; // convert units to microsteps/us^2
            this->current_spd = max(this->current_spd - spd_delta,min(this->current_spd + spd_delta, this->spd_setpoint));
            this->last_accel_update = timenow; 

            // Serial.println(micros() - this->last_spd_chg);
            this->fine_pos_setpoint = this->pos_last_spd_chg + (this->current_spd * (timenow - this->last_spd_chg));
            this->pos_setpoint = long(this->fine_pos_setpoint);
        }
            
        // check if steps need to be taken
        if (this->stepcount > this->pos_setpoint) {
            digitalWrite(this->dir_pin, LOW);
            this->is_step = true;
            this->is_forward = false;
        } else if (this->stepcount < this->pos_setpoint) {
            digitalWrite(this->dir_pin, HIGH);
            this->is_step = true;
            this->is_forward = true;
        } else {
            this->is_step = false;
        }

        // perform stepping in non-blocking manner
        if (this->is_step && !this->is_step_high && (micros() > (this->last_step + this->pulse_time))) {
            // step happens here
            digitalWrite(this->step_pin, HIGH);
            this->is_step_high = true;
            this->last_step = micros();
            this->stepcount += this->is_forward ? 1:-1;
        } else if(micros() > (this->last_step + this->pulse_time)){
            digitalWrite(this->step_pin, LOW);
            this->is_step_high = false;
            this->last_step = micros();  
        } 
    }

    long Stepper::get_stepcount() {
        return this->stepcount;
    }

    long Stepper::get_pos_setpoint() {
        // Serial.println(String(this->fine_pos_setpoint) + "\t" + String(this->current_spd * (micros() - this->last_spd_chg)));
        return this->pos_setpoint;
    }

    double Stepper::get_spd_setpoint() {
        /* 
        Returns target speed of motor in microsteps/s
        */
        return 1e6 * this->spd_setpoint;
    }
    
    double Stepper::get_speed() {
        /* 
        Returns current speed of motor in microsteps/s
        */
        return 1e6 * this->current_spd;
    }

}