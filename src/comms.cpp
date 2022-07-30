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
                // valid numeric character
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
            } else if (inChar == 'c') { // command detected
                return 1; // did not actually parse data
            }
        }
        return 1;
    }

    int writeln(String input) {
        /*
        returns: 0 if successful, 1 otherwise
        input should NOT contain '\n' character
        */
        if (!PI_SERIAL){return 1;}

        int result = PI_SERIAL.println(input);
        return result;
    }

    int write_telemetry(uint32_t time,
                        float * obj_pos,
                        double target_spd_x, double target_spd_y,
                        double curr_spd_x, double curr_spd_y,
                        long stepcount_x, long stepcount_y,
                        double x_int, double y_int) {
        /*
        returns: 0 if successful, 1 otherwise
        */
        return writeln( String(time) + "," +
                        String(obj_pos[0], TELEMETRY_DP) + "," + String(obj_pos[1], TELEMETRY_DP) + "," +
                        String(target_spd_x, TELEMETRY_DP) + "," + String(target_spd_y, TELEMETRY_DP) + "," +
                        String(curr_spd_x, TELEMETRY_DP) + "," + String(curr_spd_y, TELEMETRY_DP) + "," +
                        String(stepcount_x) + "," + String(stepcount_y) + "," +
                        String(x_int, TELEMETRY_DP) + "," + String(y_int, TELEMETRY_DP));
    }

}