#include <comms.h>

namespace Comms {
    
    const uint32_t timeout = 5; 

    int parse(float *output) {

        /*
        you should only call this if serial.available
        returns: 0 if successful, 1 otherwise 
        */
        if (!PI_SERIAL.available()){return 1;}
        
        String inString = "";
        uint32_t t0 = millis();

        while(millis() - t0 < timeout){
            char inChar = PI_SERIAL.read();
            if (isDigit(inChar) || inChar=='-' || inChar=='.') {
                // valid alphanumeric character
                inString += inChar;
                // Serial.println(inString);
            } else if (inChar == ',' || inChar == '\n') {
                float result = inString.toFloat();
                if(result == 0){
                    // unsuccessful
                    return 1;
                }
                output[(inChar==',') ? 0:1] = result;
                inString = "";
                if (inChar == '\n') {return 0;}
            }
        }
        return 1;
    }

}