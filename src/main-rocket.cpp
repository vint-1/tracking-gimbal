#include <Arduino.h>
#include <util.h>
#include <config.h>
#include <stepper.h>
#include <comms.h>

#define MODE_JOYSTICK 1
#define MODE_TRACK 2

String inString = "";
double setpoint_x = 0;
double setpoint_y = 0;
unsigned long lastPrint = 0;

unsigned long last_obj_update;
// double speed_const = 12800/512;
double speed_const = 6400/512.0; // (micro)steps per sec per analogRead unit
// double speed_const = 1600e-6/512; // (micro)steps per microsec per analogRead unit

Stepper::Stepper x_motor(XSTEP_PIN, XDIR_PIN, PULSE_TIME);
Stepper::Stepper y_motor(YSTEP_PIN, YDIR_PIN, PULSE_TIME);
// StepControl pos_controller;
// StepControl<> pos_controller(PULSE_TIME, UPDATE_PERIOD);
// RotateControl spd_controller(PULSE_TIME, UPDATE_PERIOD);

float star_pos[2]; // stores x,y star position 
float star_setpoint[2] = {360.0, 480.0}; // x,y setpoint for star position 

// double k_xp = 24.0; // (microsteps/s)
// double k_yp = 14.4; 
// double k_xi = 3.0; 
// double k_yi = 1.8;

double k_xp = 12.0; // (microsteps/s)
double k_yp = 7.2; 
double k_xi = 1.5; 
double k_yi = 0.9;

// double k_xp = 1.0; // (microsteps/s)
// double k_yp = 0.6; 
// double k_xi = 0.25; 
// double k_yi = 0.15;

double x_int = 0.0;
double y_int = 0.0;

int mode = MODE_JOYSTICK;

void reset_pid() {
    x_int = 0;
    y_int = 0;
    last_obj_update = micros();
}

void setup() {

    // Run at 1/16 microsteps
    initPinmode();
    setMS(16, YM1_PIN, YM2_PIN);
    setMS(16, XM1_PIN, XM2_PIN);

    // Initializing motor objects
    // x_motor.setMaxSpeed(MAX_SPEED);
    // y_motor.setMaxSpeed(MAX_SPEED);
    // x_motor.setAcceleration(MAX_ACCEL);
    // y_motor.setAcceleration(MAX_ACCEL);

    // Setting direction pins
    digitalWrite(XDIR_PIN, LOW);
    digitalWrite(YDIR_PIN, LOW);

    // Pi Serial
    PI_SERIAL.begin(BAUD_RATE);

    delay(500);

    // Misc. things
    lastPrint = millis();
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("hello");
    reset_pid();
} 

void loop() {

    
    unsigned long t = micros();

    if (mode == MODE_JOYSTICK) {

        // setpoint_x += normalizeInput(analogRead(STICK_X)) * speed_const * dt; 
        // setpoint_y -= normalizeInput(analogRead(STICK_Y)) * speed_const * dt; 

        // x_motor.set_pos_target(long(setpoint_x));
        // y_motor.set_pos_target(long(setpoint_y));

        x_motor.set_spd_target(normalizeInput(analogRead(STICK_Y)) * speed_const);
        y_motor.set_spd_target(normalizeInput(analogRead(STICK_X)) * speed_const);

        if (millis() >= (lastPrint + 100)){
            // Serial.println(String(millis()) + "\tx: " + String(x_motor.get_pos_setpoint()) + "\t" + String(x_motor.get_stepcount()) + "\t" + String(x_motor.get_speed()) + "\ty: " + String(y_motor.get_pos_setpoint()) + "\t" + String(y_motor.get_stepcount()) + "\t" + String(y_motor.get_speed()));
            Serial.print(x_motor.get_speed()); Serial.print("\t"); Serial.println(y_motor.get_speed());
            lastPrint = millis();
        }
    
    } else if (mode == MODE_TRACK) {
        if (PI_SERIAL.available()){
            digitalWrite(LED_BUILTIN, HIGH);
            if (!Comms::parse(star_pos)) {
                // successfully parsed
                // Serial.print(dt/1000); Serial.print(star_pos[0]); Serial.print("\t"); Serial.print(x_motor.get_speed()); 
                // Serial.print("\t"); Serial.print(star_pos[1]); Serial.print("\t"); Serial.print(y_motor.get_speed()); Serial.print('\n');
                
                if (star_pos[0] < 0 || star_pos[1] < 0) {
                    // object not detected - stop moving
                    x_motor.set_spd_target(0);
                    y_motor.set_spd_target(0);
                }

                else {
                    // compute proportional terms
                    double x_err = star_pos[0] - star_setpoint[0];
                    double y_err = star_pos[1] - star_setpoint[1];
                    double x_prop = k_xp * x_err;
                    double y_prop = k_yp * y_err;

                    // update integrators
                    unsigned long dt = t-last_obj_update;
                    double antiwindup_thresh = MAX_SPEED/64.0;
                
                    // improved anti-windup
                    // if (abs(x_prop) <= antiwindup_thresh || (x_err * x_int < 0)) {
                    //     x_int += x_err * (dt / 1.0e6) * k_xi;
                    // }

                    // if (abs(y_prop) <= antiwindup_thresh || (y_err * y_int < 0)) {
                    //     y_int += y_err * (dt / 1.0e6) * k_yi;
                    // }

                    x_int += x_err * (dt / 1.0e6) * k_xi;
                    x_int = max(-antiwindup_thresh, min(antiwindup_thresh, x_int)); // anti-windup by clamping integrator
                    y_int += y_err * (dt / 1.0e6) * k_yi;
                    y_int = max(-antiwindup_thresh, min(antiwindup_thresh, y_int)); // anti-windup by clamping integrator

                    x_motor.set_spd_target((k_xp * x_err) + x_int);
                    y_motor.set_spd_target((k_yp * y_err) + y_int);
                }
                
                last_obj_update = t;
            }
            digitalWrite(LED_BUILTIN, LOW);
        }

        if (millis() >= (lastPrint + 10)){
            // send telemetry
            Comms::write_telemetry( micros(), star_pos,
                                    x_motor.get_spd_setpoint(), y_motor.get_spd_setpoint(),
                                    x_motor.get_speed(), y_motor.get_speed(),
                                    x_motor.get_stepcount(), y_motor.get_stepcount(),
                                    x_int, y_int);
            lastPrint = millis(); 
        }

    }

    // logic to switch modes
    if (analogRead(STICK_BTN) < BTN_THRESH) {
        if (mode == MODE_JOYSTICK) {
            x_motor.set_spd_target(0);
            y_motor.set_spd_target(0);
            mode = MODE_TRACK;
            Comms::writeln("trk");
            // Serial.println("Switched to tracking mode");
            digitalWrite(LED_BUILTIN, LOW);
            reset_pid();
        } else if (mode == MODE_TRACK) {
            x_motor.set_spd_target(0);
            y_motor.set_spd_target(0);
            mode = MODE_JOYSTICK;
            Comms::writeln("acq");
            // Serial.println("Switched to manual acquisition mode");
            digitalWrite(LED_BUILTIN, HIGH);
        }
        delay(200);
        while(analogRead(STICK_BTN) < BTN_THRESH){
            x_motor.update();
            y_motor.update();
        }
        delay(200);
    }

    x_motor.update();
    y_motor.update();
  
}

