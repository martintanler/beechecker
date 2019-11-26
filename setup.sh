#!/bin/bash 
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get install sqlite3
sudo apt-get install python3-pip
sudo python3 -m pip install --upgrade pip setuptools wheel
sudo pip3 install requests
cd /home/pi
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd Adafruit_Python_DHT
sudo python3 setup.py install
cd ..
