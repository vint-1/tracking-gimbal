#pragma once
#include <Arduino.h>
#define PI_SERIAL Serial7
#define BAUD_RATE 115200

namespace Comms {
    int parse(float *output);
}