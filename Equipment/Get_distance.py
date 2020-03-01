import serial
import time
## dmesg | grep tty


def get_measurement():
    try:
        ser.write(''.encode())
        time.sleep(0.5)
        ser.write('DM\r'.encode())
        time.sleep(0.5)
        data = float(ser.read_all().decode("utf-8").splitlines()[0][1:-3])
    except:
        data = -1
    return data


def reset():
    ser.write(''.encode())
    time.sleep(0.5)
    ser.write('PR\r'.encode())


ip = '/dev/ttyUSB2'
ser = serial.Serial(ip)
ser.baudrate = 19200

while(True):
    read = ser.read_all().decode("utf-8").splitlines()
    time.sleep(0.5)
    try:
        print(read[1][1:-2])
    except:
        print("Bad target")

