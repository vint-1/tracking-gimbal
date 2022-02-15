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

unsigned long t2;
// double speed_const = 12800e-6/512;
double speed_const = 6400e-6/512; // (micro)steps per microsec per analogRead unit
// double speed_const = 1600e-6/512; // (micro)steps per microsec per analogRead unit

Stepper::Stepper x_motor(XSTEP_PIN, XDIR_PIN, PULSE_TIME);
Stepper::Stepper y_motor(YSTEP_PIN, YDIR_PIN, PULSE_TIME);
// StepControl pos_controller;
// StepControl<> pos_controller(PULSE_TIME, UPDATE_PERIOD);
// RotateControl spd_controller(PULSE_TIME, UPDATE_PERIOD);

float star_pos[2]; // stores x,y star position 
float star_setpoint[2] = {480.0, 360.0}; // x,y setpoint for star position 

double k_xp = 0.5e-6;
double k_yp = 0.3e-6; 
double k_xi = 1e-12;
double k_yi = 1e-12;

int mode = MODE_JOYSTICK;

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
    t2 = micros();
} 

void loop() {

    
    unsigned long t = micros();
    unsigned long dt = t-t2;

    if (mode == MODE_JOYSTICK) {

        // setpoint_x += normalizeInput(analogRead(STICK_X)) * speed_const * dt; 
        // setpoint_y -= normalizeInput(analogRead(STICK_Y)) * speed_const * dt; 

        // x_motor.set_pos_target(long(setpoint_x));
        // y_motor.set_pos_target(long(setpoint_y));

        x_motor.set_spd_target(normalizeInput(analogRead(STICK_Y)) * speed_const);
        y_motor.set_spd_target(normalizeInput(analogRead(STICK_X)) * speed_const);

        if (millis() > (lastPrint + 100)){
            Serial.println(String(millis()) + "\tx: " + String(x_motor.get_pos_setpoint()) + "\t" + String(x_motor.get_stepcount()) + "\t" + String(1e6*x_motor.get_speed()) + "\ty: " + String(y_motor.get_pos_setpoint()) + "\t" + String(y_motor.get_stepcount()) + "\t" + String(1e6*y_motor.get_speed()));
            lastPrint = millis();
        }
    
    } else if (mode == MODE_TRACK) {
        if (PI_SERIAL.available()){
            digitalWrite(LED_BUILTIN, HIGH);
            if (!Comms::parse(star_pos)) {
                // successfully parsed
                Serial.print(dt/1000); Serial.print(star_pos[0]); Serial.print("\t"); Serial.print(x_motor.get_speed()); 
                Serial.print("\t"); Serial.print(star_pos[1]); Serial.print("\t"); Serial.print(y_motor.get_speed()); Serial.print('\n');
                x_motor.set_spd_target(-k_xp * (star_setpoint[0] - star_pos[0]));
                y_motor.set_spd_target(-k_yp * (star_setpoint[1] - star_pos[1]));
            }
            digitalWrite(LED_BUILTIN, LOW);
        }
    }

    // logic to switch modes
    if (analogRead(STICK_BTN) < BTN_THRESH) {
        if (mode == MODE_JOYSTICK) {
            x_motor.set_spd_target(0);
            y_motor.set_spd_target(0);
            mode = MODE_TRACK;
            Serial.println("Switched to closed-loop tracking mode");
            digitalWrite(LED_BUILTIN, LOW);
        } else if (mode == MODE_TRACK) {
            x_motor.set_spd_target(0);
            y_motor.set_spd_target(0);
            mode = MODE_JOYSTICK;
            Serial.println("Switched to manual mode");
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

    t2 = t;
  
}

