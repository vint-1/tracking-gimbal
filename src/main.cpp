#include <Arduino.h>
#include <util.h>
#include <config.h>

String inString = "";
double setpoint_x = 0;
long stepcount_x = 0;
double setpoint_y = 0;
long stepcount_y = 0;
unsigned long lastStep_x = 0;
unsigned long lastStep_y = 0;
unsigned long lastPrint = 0;
unsigned long pulseTime = 50; // in us, min is 40
//unsigned long stepTime = 100; // in us, min is 80
bool isStep_x = false;
bool isForward_x = true; // +/- 1
bool isStep_y = false;
bool isForward_y = true; // +/- 1

unsigned long t2;
double speed_const = 6400e-6/512; // (micro)steps per microsec per analogRead unit
//double speed_const = 1600e-6/512; // (micro)steps per microsec per analogRead unit

// Stepper x_motor(XSTEP_PIN, XDIR_PIN);
// Stepper y_motor(YSTEP_PIN, YDIR_PIN);
// StepControl pos_controller;
// StepControl<> pos_controller(PULSE_TIME, UPDATE_PERIOD);
// RotateControl spd_controller(PULSE_TIME, UPDATE_PERIOD);

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

    delay(500);

    // Misc. things
    lastStep_x = micros();
    lastStep_y = micros();
    lastPrint = millis();
    digitalWrite(LED_BUILTIN,HIGH);
    Serial.println("hello");
    t2 = micros();
} 

void loop() {

    unsigned long t = micros();
    unsigned long dt = t-t2;
    setpoint_x += normalizeInput(analogRead(STICK_X)) * speed_const * dt; 
    setpoint_y -= normalizeInput(analogRead(STICK_Y)) * speed_const * dt; 

    // x_motor.setTargetAbs(setpoint_x);
    // y_motor.setTargetAbs(setpoint_y);

    if (millis() > (lastPrint + 250)){
        Serial.println(String(millis()) + "\tx: " + String(setpoint_x) + "\t" + String(stepcount_x) + "\ty: " + String(setpoint_y) + "\t" + String(stepcount_y));
        lastPrint = millis();
    }

    t2 = t;
  
}

