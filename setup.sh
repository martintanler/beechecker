#!/bin/bash 
cd /home/pi
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 setup.py install
cd ..
