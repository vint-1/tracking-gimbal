#include <Arduino.h>

#define YSTEP_PIN 20
#define YDIR_PIN 21
#define XSTEP_PIN 40
#define XDIR_PIN 41

#define SLEEP_PIN 8

#define YM1_PIN 16
#define YM2_PIN 17
#define XM1_PIN 36
#define XM2_PIN 37

#define STICK_X 27
#define STICK_Y 26

void initPinmode(){
  pinMode(YSTEP_PIN,OUTPUT);
  pinMode(YDIR_PIN,OUTPUT);
  pinMode(XSTEP_PIN,OUTPUT);
  pinMode(XDIR_PIN,OUTPUT);
  pinMode(SLEEP_PIN,OUTPUT);
  pinMode(YM1_PIN,OUTPUT);
  pinMode(YM2_PIN,OUTPUT);
  pinMode(XM1_PIN,OUTPUT);
  pinMode(XM2_PIN,OUTPUT);
  pinMode(STICK_X, INPUT);
  pinMode(STICK_Y, INPUT);
}