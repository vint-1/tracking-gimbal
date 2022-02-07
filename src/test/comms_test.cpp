#pragma once
#include <Arduino.h>
#include <comms.h>

void setup(){
    while(!Serial);
    Serial.println("starting serial comms test");
    PI_SERIAL.begin(BAUD_RATE);
}

float star_pos[2];

void loop(){
    // PI_SERIAL.println("hello there, this is teensy speaking");
    if (PI_SERIAL.available()){
        uint32_t t0 = millis();
        if (!Comms::parse(star_pos)) {
            // successfully parsed
            Serial.print(millis()-t0); Serial.print("\t");Serial.print(star_pos[0]*10.0); Serial.print("\t"); Serial.print(star_pos[1]*100.0); Serial.print('\n');
        } else {
            Serial.println("parsing fucked up");
        }
    }
    // delay(100);
}