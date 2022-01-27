#include <Arduino.h>
#include <util.h>
#include <config.h>

String inString = "";
double setpont_x = 0;
long stepcount_x = 0;
double setpont_y = 0;
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

void setup() {
  // put your setup code here, to run once:
  // run at 16 microsteps
  initPinmode();
  setMS(16, YM1_PIN, YM2_PIN);
  setMS(16, XM1_PIN, XM2_PIN);
  delay(500);
  lastStep_x = micros();
  lastStep_y = micros();
  lastPrint = millis();
  Serial.println("hello");
  digitalWrite(13,HIGH);
  digitalWrite(XDIR_PIN, LOW);
  digitalWrite(YDIR_PIN, LOW);
  t2 = micros();
} 

void loop() {
  // put your main code here, to run repeatedly:

  unsigned long t = micros();
  unsigned long dt = t-t2;
  setpont_x += normalizeInput(analogRead(STICK_X)) * speed_const * dt; 
  setpont_y -= normalizeInput(analogRead(STICK_Y)) * speed_const * dt; 
  
  if(stepcount_x > long(setpont_x)){
    digitalWrite(XDIR_PIN, LOW);
    isStep_x = true;
    isForward_x = false;
  } else if (stepcount_x < long(setpont_x)){
    digitalWrite(XDIR_PIN, HIGH);
    isStep_x = true;
    isForward_x = true;
  } else {
    isStep_x = false;
  }

  if(stepcount_y > long(setpont_y)){
    digitalWrite(YDIR_PIN, LOW);
    isStep_y = true;
    isForward_y = false;
  } else if (stepcount_y < long(setpont_y)){
    digitalWrite(YDIR_PIN, HIGH);
    isStep_y = true;
    isForward_y = true;
  } else {
    isStep_y = false;
  }

  
  if (isStep_x && (micros() > (lastStep_x + pulseTime))) {
    // step happens here
    digitalWrite(XSTEP_PIN, HIGH);
    lastStep_x = micros();
    stepcount_x += isForward_x ? 1:-1;
  } else if(micros() > (lastStep_x + pulseTime)){
    digitalWrite(XSTEP_PIN, LOW);
    lastStep_x = micros();  
  } 

  if (isStep_y && (micros() > (lastStep_y + pulseTime))) {
    // step happens here
    digitalWrite(YSTEP_PIN, HIGH);
    lastStep_y = micros();
    stepcount_y += isForward_y ? 1:-1;
  } else if(micros() > (lastStep_y + pulseTime)){
    digitalWrite(YSTEP_PIN, LOW);
    lastStep_y = micros();  
  } 

  if (millis() > (lastPrint + 250)){
    Serial.println(String(millis()) + "\t" + String(setpont_y) + "\t" + String(stepcount_y) + "\t" + String(isStep_y));
    lastPrint = millis();
  }
  
  while (Serial.available() > 0) {
        //Read incoming commands
        int inChar = Serial.read();
        
        if (inChar == '\n') {
            if (inString[0]=='m') { //change step size
              setMS(inString.substring(1).toInt(), XM1_PIN, XM2_PIN);
              setMS(inString.substring(1).toInt(), YM1_PIN, YM2_PIN);
              Serial.println("Changing step size to " + inString.substring(1));
            }
            inString = "";
        } else {
            inString += (char)inChar;
        }
        
  }

  t2 = t;
  
}

