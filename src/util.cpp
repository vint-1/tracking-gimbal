#pragma once
#include <util.h>

void setMS(int m, int m1_pin, int m2_pin){ //sets output to achieve desired microstep rate
  if(m==2){ //half step
    digitalWrite(m1_pin,LOW);
    digitalWrite(m2_pin,HIGH);
  }
  else if(m==4){ 
    digitalWrite(m1_pin,HIGH);
    digitalWrite(m2_pin,LOW);
  }
  else if(m==8){ 
    digitalWrite(m1_pin,LOW);
    digitalWrite(m2_pin,LOW);
  }
  else if(m==16){ 
    digitalWrite(m1_pin,HIGH);
    digitalWrite(m2_pin,HIGH);
  }
}

int normalizeInput(int raw){
  // normalizes input
  const int dead_low = 450;
  const int dead_hi = 590;
  if (raw <= dead_low) {
    return raw-dead_low;
  } else if (raw >= dead_hi) {
    return raw-dead_hi;
  } else {
    return 0;
  }
}