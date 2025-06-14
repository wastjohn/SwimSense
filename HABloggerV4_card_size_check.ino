/*
High altitude balloon data logger
D.Bailey, Macalester College, 10/20/2024

Portions of the code below adapted from various code examples provided by Adafruit, LLC 
Written for Adafruit Adalogger Feather M0
Other modules included are the Adafruit Ultimate GPS and the MS8607 (pressure, humidity, and temp)
External temperature sensor is an Analog Devices TMP36 housed in a T0-92 form factor
*/

//adjustable parameters
#define dataLogInterval 2       //in seconds, miminum interval is 1 second, enter integers only
#define dataFlushThreshold 30  //the number of data rows to store before flushing out to SD card
float batteryLowThreshold = 3.6;  //set low voltage limit in volts, value can be floating, stay above 3.5V to be safe


//do not change anything from this point on
#define cardDetectPin 7        //SD card presence switch
#define greenLEDPin 8          //SD card write/unmounted indicator
#define redLEDPin 13           //data logging start indicator
#define startButton 6          //start/eject button pin
#define holdTime 2000          //hold time for start button press
#define VBATPIN A7             //battery voltage sense pin Adalogger M0
#define sensorPin 0            //the analog pin the TMP36's Vout (sense) pin is connected to \
                         //the resolution is 10 mV / degree centigrade with a \
                         //500 mV offset to allow for negative temperatures

//SD card setup
#include <SPI.h>
#include <SdFat.h>
SdFat SD;       //SdFat class instance
File dataFile;  //file class instance

//MS8607 pressure and temp sensor setup
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_MS8607.h>
Adafruit_MS8607 ms8607; //MS8607 class instance

//GPS sensor output setup
#include <Adafruit_GPS.h>
#define GPSSerial Serial1
Adafruit_GPS GPS(&GPSSerial);  //GPS class instance
#define GPSECHO false

//external temp sensor value
float exTemp;

//other global variables
bool stopLED = false;
unsigned long timePressed = 0;

float measuredvbat = 0;
uint32_t timer = millis();
int logCount = 0;  //counter variable for data flush

//functions

void waitForStartButton() {  //wait until the button is pressed for 2 seconds
  while (true) {
    if (digitalRead(startButton) == LOW) {  //button is pressed
      if (timePressed == 0) {
        timePressed = millis();                         //start timing the button press
      } else if (millis() - timePressed >= holdTime) {  //button has been pressed for 2 seconds, return from loop
        timePressed = 0;
        for (int x = 0; x < 3; x++) {
          digitalWrite(redLEDPin, HIGH);
          delay(500);
          digitalWrite(redLEDPin, LOW);
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

void noCard() {  //no card detect function
  while (1) {
    digitalWrite(greenLEDPin, millis() % 500 > 250);  //strobe green LED on and off every half second, indicates card is missing
  }
}

void cardError() {
  while (1) {
    digitalWrite(redLEDPin, millis() % 500 > 250);  //strobe green LED on and off every half second, indicates card is missing
  }
}

void closeSDcard() {  //close file function
  dataFile.close();
  delay(200);
  digitalWrite(greenLEDPin, HIGH);
  while (1) {
    digitalWrite(greenLEDPin, millis() % 500 > 250);  //halt program flash green LED on and off every half second, indicates card not mounted
  }
}

void getExternalTemp() {
  int reading = analogRead(sensorPin);
  float voltage = reading * 3.3;  //converting that reading to voltage, for 3.3v arduino use 3.3
  voltage /= 1023.0;
  float temperatureC = (voltage - 0.5) * 100;  //converting from 10 mv per degree wit 500 mV offset
                                               //to degrees ((voltage - 500mV) times 100)
  exTemp = temperatureC;
}

void batteryCheck() {
  measuredvbat = analogRead(VBATPIN);  //battery voltage pin
  measuredvbat *= 2;                   //we divided by 2, so multiply back
  measuredvbat *= 3.3;                 //multiply by 3.3V, our reference voltage
  measuredvbat /= 1024;                //convert to voltage
  if (measuredvbat < batteryLowThreshold) {
    //Serial.println("battery low");
    closeSDcard();
  }
}


//setup
void setup() {
  Serial.begin(115200);
  pinMode(cardDetectPin, INPUT_PULLUP);  //onboard card presence switch
  pinMode(startButton, INPUT_PULLUP);    //external board switch
  pinMode(greenLEDPin, OUTPUT);          //onboard green LED, pin 8
  pinMode(redLEDPin, OUTPUT);            //onboard red led, pin 13

  if (!SD.begin(4, SPI_HALF_SPEED)) noCard();
  batteryCheck();
  waitForStartButton();             //call the function to wait for a 2-second button press to start logging
  if (!SD.exists("HABdata.csv")) {  //create the file if it doesn't already exist
    dataFile = SD.open("HABdata.csv", FILE_WRITE);
  } else {
    dataFile = SD.open("HABdata.csv", FILE_WRITE | O_APPEND);  //append to existing file, mark as "new session"
    if (dataFile) {
      dataFile.println(" ");
      dataFile.print("New session");
      dataFile.print("\n");
      //Serial.print("\n");
    }
  }

  //GPS config
  GPS.begin(9600);
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  delay(1000);
  GPSSerial.println(PMTK_Q_RELEASE);


  //pressure and temp sensor config
  if (!ms8607.begin()) {
    // Serial.println("Failed to find MS8607 chip");
    while (1) { delay(10); }
    // Serial.print("ms8607 found!");
  }
  ms8607.setHumidityResolution(MS8607_HUMIDITY_RESOLUTION_OSR_8b);    //not used but setup is necessary
  ms8607.setPressureResolution(MS8607_PRESSURE_RESOLUTION_OSR_4096);  //set to 12 bit resolution
}

//main loop
void loop() {
  if (!digitalRead(cardDetectPin)) {
    //Serial.println("card improperly ejected");
    cardError();
  }
  batteryCheck(); //make sure battery level is good
  if (digitalRead(startButton) == LOW) {  //button is pressed
    if (timePressed == 0) {
      timePressed = millis();
    } else if (millis() - timePressed >= holdTime) {  //button has been pressed for 2 seconds, exit the loop and close SD card
      closeSDcard();
    }
  } else {
    timePressed = 0;  //reset time if button is released before 2 seconds
  }

  // Check if there is enough space on the SD card before continuing
  uint32_t freeSpace = SD.freeClusterCount();  // Get the available clusters on the SD card
  if (freeSpace < 2) {  // Example: if fewer than 2 clusters are available, the card is nearly full
    // Handle SD card full condition: close the SD card and halt further operations
    closeSDcard();
  }


  //GPS data read
  char c = GPS.read();  //read data from the GPS in the 'main loop'
  if (GPS.newNMEAreceived()) {
    char c = GPS.read();
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trying to print out data
    //Serial.print(GPS.lastNMEA());  //this also sets the newNMEAreceived() flag to false
    if (!GPS.parse(GPS.lastNMEA()))  //this also sets the newNMEAreceived() flag to false
      return;                        //we can fail to parse a sentence in which case we should just wait for another
  }

//logging
  if (millis() - timer > dataLogInterval * 1000) {  //every x seconds, record data
    digitalWrite(greenLEDPin, HIGH);  //turn on uSD card write LED
    timer = millis();                 //reset the timer
    // if (!GPS.fix) {
    //   dataFile.print("\n");
    //   //Serial.print("\n");
    // }
    if (GPS.hour < 10) {
      dataFile.print('0');
      //Serial.print('0');
    }
    dataFile.print(GPS.hour, DEC);
    //Serial.print(GPS.hour, DEC);
    dataFile.print(":");
    // Serial.print(":");
    if (GPS.minute < 10) {
      dataFile.print('0');
      //Serial.print('0');
    }
    dataFile.print(GPS.minute, DEC);
    //Serial.print(GPS.minute, DEC);
    dataFile.print(":");
    //Serial.print(":");
    if (GPS.seconds < 10) {
      dataFile.print('0');
      //Serial.print('0');
    }
    dataFile.print(GPS.seconds, DEC);
    //Serial.print(GPS.seconds, DEC);
    dataFile.print(",");
    //Serial.print(", ");
    dataFile.print(GPS.day, DEC);
    //Serial.print(GPS.day, DEC);
    dataFile.print('/');
    //Serial.print('/');
    dataFile.print(GPS.month, DEC);
    //Serial.print(GPS.month, DEC);
    dataFile.print("/20");
    //Serial.print("/20");
    dataFile.print(GPS.year, DEC);
    //Serial.print(GPS.year, DEC);
    dataFile.print(",");
    //Serial.print(", ");

    //get TMP36 temperature
    getExternalTemp();
    dataFile.print(exTemp, 1);
    //Serial.print(exTemp,1);
    dataFile.print(",");
    //Serial.print(", ");

    //get MS8607 pressure and temp
    sensors_event_t temp, pressure, humidity;
    ms8607.getEvent(&pressure, &temp, &humidity);
    dataFile.print(temp.temperature, 1);
    //Serial.print(temp.temperature,1);
    dataFile.print(",");
    //Serial.print(", ");
    dataFile.print(pressure.pressure);
    //Serial.print(pressure.pressure);
    dataFile.print(",");
    //Serial.print(", ");
    dataFile.print(measuredvbat);
    //Serial.print(measuredvbat);

    //get location data when a fix is aquired
    if (GPS.fix) {
      dataFile.print(",");
      //Serial.print(", ");
      dataFile.print(GPS.latitude, 4);
      //Serial.print(GPS.latitude, 4);
      dataFile.print(GPS.lat);
      //Serial.print(GPS.lat);
      dataFile.print(",");
      //Serial.print(", ");
      dataFile.print(GPS.longitude, 4);
      //Serial.print(GPS.longitude, 4);
      dataFile.print(GPS.lon);
      //Serial.print(GPS.lon);
      dataFile.print(",");
      //Serial.print(", ");
      dataFile.print(GPS.altitude);
      //Serial.print(GPS.altitude);
    }
      dataFile.print("\n"); //start new line
      //Serial.print("\n");
    logCount++;  //increment logCount
    //Serial.println(logCount);
    if (logCount >= dataFlushThreshold) {  //flush data sitting out of buffer when count threshold is reached
      dataFile.flush(); //write any data sitting in the buffer to SD card
      logCount = 0;
    }
  }
  digitalWrite(greenLEDPin, LOW);  //write is complete, turn off onboard green LED
}