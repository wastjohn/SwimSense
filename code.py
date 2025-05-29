import board
import busio
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import BNO_REPORT_ACCELEROMETER, BNO_REPORT_GYROSCOPE, BNO_REPORT_MAGNETOMETER, BNO_REPORT_ROTATION_VECTOR
import time
import digitalio
import microcontroller
import storage
import adafruit_sdcard
import os


def waitForStartButton():
    timePressed = 0
    holdTime = 2
    while True:
        if button.value == False:  # button is pressed
            if timePressed == 0:
                timePressed = time.monotonic()
            elif time.monotonic() - timePressed >= holdTime:
                timePressed = 0
                for i in range(3):
                    led.value = True
                    time.sleep(0.5)
                    led.value = False
                    time.sleep(0.5)
                print("elapsed 2s --- ready to save to SD card")
                return
        else:
            timePressed = 0



def collectData():
    t = 0
    dt = 0.01
    f = open("/sd/sensor_data.txt", "a")
    timePressed = 0
    holdTime = 2
    while True:
        if button.value == False:  # button is pressed
            if timePressed == 0:
                timePressed = time.monotonic()
            elif time.monotonic() - timePressed >= holdTime:
                timePressed = 0
                for i in range(3):
                    led.value = True
                    time.sleep(0.5)
                    led.value = False
                    time.sleep(0.5)
                print("elapsed 2s --- closing SD card")
                f.close()
                return
        else:
            timePressed = 0
            accel_x, accel_y, accel_z = bno.acceleration
            gyro_x, gyro_y, gyro_z = bno.gyro
            mag_x, mag_y, mag_z = bno.magnetic
            quat_i, quat_j, quat_k, quat_real = bno.quaternion
            now = time.monotonic()
            f.write("%0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f\n" % (now, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, quat_i, quat_j, quat_k, quat_real))
            led.value = True
            time.sleep(dt)
            led.value = False
            t = now
            #print("saving to txt: %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f" % (now, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, quat_i, quat_j, quat_k, quat_real))


# define the led and boot button
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
button = digitalio.DigitalInOut(board.BUTTON)
button.switch_to_input(pull=digitalio.Pull.UP)


# main part
while True:
    waitForStartButton()
    print("STARTING UP...")
    time.sleep(1)
    
    # Connect to the card and mount the filesystem.
    print("Connected to card and mounted on filesystem...")
    cs = digitalio.DigitalInOut(board.SD_CS)
    sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
    sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")
    print("COMPLETE")
    
    
    # connect to the BNO sensor
    print("Connecting to BNO sensor...")
    i2c = busio.I2C(board.SCL, board.SDA)
    bno = BNO08X_I2C(i2c)
    bno.enable_feature(BNO_REPORT_ACCELEROMETER)
    bno.enable_feature(BNO_REPORT_GYROSCOPE)
    bno.enable_feature(BNO_REPORT_MAGNETOMETER)
    bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)
    print("COMPLETE")

    # create the txt file
    print(os.listdir("/sd/"))
    if "sensor_data.txt" not in os.listdir("/sd/"):
        print("SD CARD NOT FOUND")
        file = open("/sd/sensor_data.txt", "w")
        file.close()
        print("FILE CREATED")

    print("Saving to SD card, hold button for 2s to stop and eject the card")
    # read the sensor data and save to txt file
    collectData()
    print("Finished collecting data")
    
