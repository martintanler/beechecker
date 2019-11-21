from datetime import datetime as dt
from at.tama.beechecker.dbaccess import DbAccess
import Adafruit_DHT as dht
from at.tama.beechecker.configuration.hx711 import HX711
import RPi.GPIO as GPIO
from at.tama.beechecker.sensor.hivedata import HiveData
from at.tama.beechecker.restclient import RestClient


def clean():
    print ("Cleaning...")
    GPIO.cleanup()
    print ("Cleaned!")

def read_temp(temp_sensor):
    if temp_sensor.get_product() == 'DHT22':
        return dht.read_retry(dht.DHT22, int(temp_sensor.get_bcm()))
    elif temp_sensor.get_product() == 'DHT11':
        return dht.read_retry(dht.DHT11, int(temp_sensor.get_bcm()))
    else:
        print('Unsupported product ', temp_sensor.get_product())


hives = DbAccess.find_hives()

beekeeper = DbAccess.find_beekeeper()
if beekeeper is not None:
    for hive in hives:
        curr_time = dt.now()
        hive_data = HiveData()
        hive_data.set_id_beehive(hive.get_id())
        hive_data.set_hive_bezeichnung(hive.get_name())
        hive_data.set_sored_at(curr_time)
        if hive.get_calibrated() and hive.get_weight().get_bcm() is not None:
            try:
                calibration = DbAccess.find_hive_calibration(hive.get_name())
                pins = hive.get_weight().get_bcm().split(",")
                data_pin = pins[0]
                clk_pin = pins[1]
                hx = HX711(int(data_pin), int(clk_pin), gain=128)
                hx.set_reading_format("LSB", "MSB")
                #print('_reference_unit:', calibration.value_per_gram)
                hx.set_reference_unit(calibration.value_per_gram)
                hx.reset()
                #print('_offset:', calibration.offset)
                hx.set_offset(calibration.offset)
                hive_data.set_weight(hx.get_weight(5)/1000)
                clean()
            except Exception as e:
                clean()

        if hive.get_temperature_inside().get_bcm() is not None and hive.get_temperature_inside().get_product() is not None:
            try:
                humidity, temp = read_temp(hive.get_temperature_inside())
                hive_data.set_humidity_in(humidity)
                hive_data.set_temp_in(temp)
                clean()
            except Exception as e:
                clean()

        if hive.get_temperature_outside().get_bcm() is not None and hive.get_temperature_outside().get_product() is not None:
            try:
                humidity, temp = read_temp(hive.get_temperature_outside())
                hive_data.set_humidity_out(humidity)
                hive_data.set_temp_out(temp)
                clean()
            except Exception as e:
                clean()

        DbAccess.persist_hive_data(hive_data)
        RestClient.put_sensor_data(hive_data, beekeeper.get_token())
        hive_data.set_sent_at(curr_time)
        DbAccess.persist_hive_data(hive_data)


