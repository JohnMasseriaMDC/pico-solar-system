# Pico Solar System

A miniature device depicting the relative position of the planets in Solar System.

![pico](docs/pico_s.jpeg)

### Hardware
* Raspberry Pi Pico
* Precision RTC Module (DS3231)
* Pico Display Pack


### Software
#### MicroPython
The software is written in MicroPython 1.15 and uses a custom build from Pimorony which includes drivers for the display.
Download it from the official Pimorony repository [here](https://github.com/pimoroni/pimoroni-pico/releases/tag/v0.2.1).

1. Download the MicroPython UF2.
2. Push and hold the BOOTSEL button and plug your Pico into the USB port of your computer. Release the BOOTSEL button after your Pico is connected.
3. It will mount as a Mass Storage Device called RPI-RP2.
4. Drag and drop the MicroPython UF2 file onto the RPI-RP2 volume. 

#### rshell
To upload and configure your Pico Solar System you will need to install rshell. Make sure you have _pip_ installed.
```
pip3 install rshell
```

#### Installing Pico Solar System
1. Download Pico Solar System
```
git clone https://github.com/dr-mod/pico-solar-system.git
```
2. Open the directory with the source code
```
cd pico-solar-system
```
3. Copy required python files to your pico
```
rshell
cp *.py /pyboard/
```
4. Set time & configure the RTC module 
```
repl

import time
import ds3231
rtc = ds3231.ds3231()
rtc.set_time(time.time())
```

### Support the project
If you would like to support further development of this or any new projects that I make, consider donating:
```
BTC:    36Z9R2mQVdeN58GpGwE7VW6Zjk6yK4MptD
ETH:    0x13992b783fbb1ff3a2cc04f2fac04691614bd68e
DOGE:   DLW5joMTi8Vm5a1frZHgW8LcPWo4oLqfUZ
LTC:    LiZTtdgqALLbU5YkYkBzhBFHSsvBv2Ghot
```