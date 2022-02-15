#pragma once
#include <Arduino.h>
#include <comms.h>

void setup(){
    // while(!Serial);
    Serial.println("starting serial comms test");
    PI_SERIAL.begin(BAUD_RATE);
}

float star_pos[2];

void loop(){
    // Test 2-way communications between teensy and Pi
    // PI_SERIAL.println("hello there, this is teensy speaking");
    if (PI_SERIAL.available()){
        uint32_t t0 = millis();
        if (!Comms::parse(star_pos)) {
            // successfully parsed
            Serial.print(millis()-t0); Serial.print("\t");Serial.print(star_pos[0]*10.0); Serial.print("\t"); Serial.print(star_pos[1]*10.0); Serial.print('\n');
        } else {
            Serial.println("parsing fucked up");
        }
    }

    // Write telemetry as fast as humanly possible
    Comms::write_telemetry(micros(), star_pos, 2.32e-3, 1.5e-1, 2e-1, -3.231e-3, 100000, -500000000);
    // delay(100);
}