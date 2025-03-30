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

# Connect to the card and mount the filesystem.
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# connect to the BNO sensor
i2c = busio.I2C(board.SCL, board.SDA)
bno = BNO08X_I2C(i2c)
bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

# create the txt file
if "sensor_data.txt" not in os.listdir("/sd/"):
    file = open("/sd/sensor_data.txt", "w")
    file.close()

# save sensor data to txt file
t = 0
dt = 0.01#
while True:
    with open("/sd/sensor_data.txt", "a") as f:
        accel_x, accel_y, accel_z = bno.acceleration
        gyro_x, gyro_y, gyro_z = bno.gyro
        mag_x, mag_y, mag_z = bno.magnetic
        quat_i, quat_j, quat_k, quat_real = bno.quaternion
        now = t + dt
        f.write("%0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f\n" % (now, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, quat_i, quat_j, quat_k, quat_real))
    time.sleep(dt)
    print(now)
    t = now
    print("saving to txt: %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f, %0.6f" % (now, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, quat_i, quat_j, quat_k, quat_real))


print(os.listdir("/sd/"))


