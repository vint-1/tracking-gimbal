#pragma once
#include <Arduino.h>
#include <comms.h>

void setup(){
    while(!Serial);
    Serial.println("starting serial comms test");
    PI_SERIAL.begin(BAUD_RATE);
}

float target[2];

void loop(){
    // PI_SERIAL.println("hello there, this is teensy speaking");
    if (PI_SERIAL.available()){
        uint32_t t0 = millis();
        if (!Comms::parse(target)) {
            // successfully parsed
            Serial.print(millis()-t0); Serial.print("\t");Serial.print(target[0]*10.0); Serial.print("\t"); Serial.print(target[1]*100.0); Serial.print('\n');
        } else {
            Serial.println("parsing fucked up");
        }
    }
    // delay(100);
}