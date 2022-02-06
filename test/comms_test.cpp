#include <Arduino.h>
#define PI_SERIAL Serial7

void setup(){
    PI_SERIAL.begin(9600)
}

void loop(){
    PI_SERIAL.println("hello there, this is teensy speaking")
    delay(100);
}