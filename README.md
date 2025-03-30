# SwimSense
Open-source software and hardware instructions for 


## Prototype
### Materials
- 1 x Adafruit Feather RP2040 Adalogger with Micro SD card
- 1 x Micro SD card
- 1 x BNO085 9-DOF Sensor
- 1 x Stemma QT connectors
- 1 x USB-C to USB-C connector (for bootloading)

### Assembly and Setup
Purchase all materials above.

#### Bootload the Microcontroller/install CircuitPython
1. Connect the microcontroller to your computer via the USB-C to USB-C cable
2. An LED on the microcontroller should light up
3. Hold the two buttons down on the microcontroller
4. The LED should change colors/flash and a new drive should pop up on your computer named RPI-RP2
5. Navigate to the latest version of CircuitPython and download the .UF2 file to your computer
6. Move the .UF2 file to the RPI-RP2 drive
7. The drive should rename itself to ‘CIRCUITPY (D:)’ and a new file structure should appear, including a code.py file

#### Test Python on the microcontroller
1. Open code.py in VS Code
2. The following code prints “hello world” every second. Copy the following code and replace the original with it in code.py

```
import time
while True:
print("hello world")
time.wait(1)
```

3. In the VS Code terminal (press CTRL+J or Command+J if not visible), navigate to the Serial Monitor tab.
4. If the microcontroller is successfully bootloaded and connected to your computer via USB-C, you should be able to choose a connection

#### Add Microcontroller Libraries
Download all folders and files inside this repo's `lib` folder and move them to the microcontroller's `lib` folder.

