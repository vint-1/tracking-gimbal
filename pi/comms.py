import serial
import time

BAUD_RATE = 9600
ser = serial.Serial("/dev/ttyS0", baudrate = BAUD_RATE, timeout = 0.01)

def write_test():
    while True:
        print(ser.write(b"hello world! This is a slightly longer message"), len("hello world! This is a slightly longer message"))
        time.sleep(0.05)

def read_test():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline()
            print(line)

def main():
    read_test()

if __name__ == "__main__":
    main()