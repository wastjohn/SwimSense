/*
File: main.ino

This script reads from a sensor and saves to an SD card.

Author: Will St. John, David Bailey
Summer 2025
*/

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>
#include "SdFat.h"

#define SD_CS_PIN 23
#define startButton PIN_BUTTON
#define led LED_BUILTIN
// #define npled PIN_NEOPIXEL
#define holdTime 2000
unsigned long timePressed = 0;

Adafruit_MPU6050 mpu;
SdFat SD;
FsFile dataFile;
SdSpiConfig config(SD_CS_PIN, DEDICATED_SPI, SD_SCK_MHZ(16), &SPI1);



//////////////// helpful functions ////////////////

void waitForStartButton() {  //wait until the button is pressed for 2 seconds
  while (true) {
    if (digitalRead(startButton) == LOW) {  //button is pressed
      if (timePressed == 0) {
        timePressed = millis();                         //start timing the button press
      } else if (millis() - timePressed >= holdTime) {  //button has been pressed for 2 seconds, return from loop
        timePressed = 0;
        for (int x = 0; x < 3; x++) {
          digitalWrite(led, HIGH);
          delay(500);
          digitalWrite(led, LOW);
          delay(500);
        }
        return;
      }
    } else {
      // Reset if button is released before 2 seconds
      timePressed = 0;
    }
  }
}




void closeSDcard() {  //close file function
  dataFile.close();
  Serial.println("Closed SD card.");
  delay(200);
  digitalWrite(led, HIGH);
  while (1) {
    digitalWrite(led, millis() % 500 > 250);  //halt program flash LED on and off every half second, indicates card not mounted
  }
}



//////////////// Microcontroller Setup ////////////////

void setup(void) {
  Serial.begin(115200);
  pinMode(led, OUTPUT);  // configure led to be able to flash
  
  Serial.println("Powered on. Waiting for start button.");
  waitForStartButton();

  while (!SD.begin(config)) {
    Serial.println("initialization failed! Retrying...");
    delay(1000); // Wait for a second before retrying
  }
  Serial.println("initialization done.");
  
  if (!SD.exists("swimdata.csv")) {  //create the file if it doesn't already exist
    dataFile = SD.open("swimdata.csv", FILE_WRITE);
  } else {
    dataFile = SD.open("swimdata.csv", FILE_WRITE | O_APPEND);  //append to existing file, mark as "new session"
    if (dataFile) {
      dataFile.println(" ");
      dataFile.print("New session");
      dataFile.print("\n");
      //Serial.print("\n");
    }
  }

  // Try to initialize!
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  Serial.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  Serial.print("Accelerometer range set to: ");
  switch (mpu.getAccelerometerRange()) {
  case MPU6050_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case MPU6050_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case MPU6050_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case MPU6050_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  Serial.print("Gyro range set to: ");
  switch (mpu.getGyroRange()) {
  case MPU6050_RANGE_250_DEG:
    Serial.println("+- 250 deg/s");
    break;
  case MPU6050_RANGE_500_DEG:
    Serial.println("+- 500 deg/s");
    break;
  case MPU6050_RANGE_1000_DEG:
    Serial.println("+- 1000 deg/s");
    break;
  case MPU6050_RANGE_2000_DEG:
    Serial.println("+- 2000 deg/s");
    break;
  }

  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  Serial.print("Filter bandwidth set to: ");
  switch (mpu.getFilterBandwidth()) {
  case MPU6050_BAND_260_HZ:
    Serial.println("260 Hz");
    break;
  case MPU6050_BAND_184_HZ:
    Serial.println("184 Hz");
    break;
  case MPU6050_BAND_94_HZ:
    Serial.println("94 Hz");
    break;
  case MPU6050_BAND_44_HZ:
    Serial.println("44 Hz");
    break;
  case MPU6050_BAND_21_HZ:
    Serial.println("21 Hz");
    break;
  case MPU6050_BAND_10_HZ:
    Serial.println("10 Hz");
    break;
  case MPU6050_BAND_5_HZ:
    Serial.println("5 Hz");
    break;
  }

  Serial.println("");
  delay(100);


}


//////////////// Data logging loop ////////////////

void loop() {
  //// Close SD card logic
  if (digitalRead(startButton) == LOW) {  //button is pressed
    if (timePressed == 0) {
      timePressed = millis();
    } else if (millis() - timePressed >= holdTime) {  //button has been pressed for 2 seconds, exit the loop and close SD card
      closeSDcard();
    }
  } else {
    timePressed = 0;  //reset time if button is released before 2 seconds
  }

  //// Check if there is enough space on the SD card before continuing
  uint32_t freeSpace = SD.freeClusterCount();  // Get the available clusters on the SD card
  if (freeSpace < 2) {  // Example: if fewer than 2 clusters are available, the card is nearly full
    // Handle SD card full condition: close the SD card and halt further operations
    closeSDcard();
  }

  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  /* Print out the values */
  Serial.print("ax:");
  Serial.print(a.acceleration.x);
  dataFile.print(a.acceleration.x);
  Serial.print(",");
  dataFile.print(",");

  Serial.print("ay:");
  Serial.print(a.acceleration.y);
  dataFile.print(a.acceleration.y);
  Serial.print(",");
  dataFile.print(",");

  Serial.print("az:");
  Serial.print(a.acceleration.z);
  dataFile.print(a.acceleration.z);
  Serial.print(",");
  dataFile.print(",");

  Serial.print("gx:");
  Serial.print(g.gyro.x);
  dataFile.print(g.gyro.x);
  Serial.print(",");
  dataFile.print(",");


  Serial.print("gy:");
  Serial.print(g.gyro.y);
  dataFile.print(g.gyro.y);
  Serial.print(",");
  dataFile.print(",");


  Serial.print("gz:");
  Serial.println(g.gyro.z);
  dataFile.println(g.gyro.z);

  dataFile.flush();
  delay(15);
}




