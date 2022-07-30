from math import sin, cos
import serial
import time

BAUD_RATE = 115200
ser = serial.Serial("/dev/serial0", baudrate = BAUD_RATE, timeout = 0.005)

def write_test():
    while True:
        print(ser.write(b"hello world! This is a slightly longer message"), len("hello world! This is a slightly longer message"))
        time.sleep(0.05)

def read_test():
    print("=== Starting read test ===")
    while True:
        if ser.in_waiting > 0:
            line = ser.readline()
            print(line)

def write_packet_test():
    while True:
        message = "120.321,-200.010\n"
        print(ser.write(bytes(message, encoding="ascii")), len(message))
        time.sleep(0.05)

def twoway_test():
    print("=== Starting twoway test ===")
    while True:
        t = time.time()
        write_coord(sin(t),cos(t))
        if ser.in_waiting > 0:
            line = read()
            print(line.split(","))

def write_coord(x, y):
    message = f"{x:.3f},{y:.3f}\n" # writes with 3 decimal precision
    ser.write(bytes(message, encoding="ascii"))

def read():
    """ 
    Reads from serial. returns None if there is nothing to read, otherwise return single line with whitespace stripped
    TODO: Handle errors gracefully
    """
    if ser.in_waiting > 0:
        try:
            raw_line = ser.readline()
            line = str(raw_line, 'ascii').strip()
            return line
        except:
            return
    return

def main():
    twoway_test()

if __name__ == "__main__":
    main()