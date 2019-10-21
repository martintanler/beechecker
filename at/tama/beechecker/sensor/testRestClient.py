from datetime import datetime as dt

from at.tama.beechecker.dbaccess import DbAccess
from at.tama.beechecker.restclient import RestClient
from at.tama.beechecker.sensor.hivedata import HiveData

testdata = {
    "token": "abc"
}
curr_time = dt.utcnow().astimezone()

hive_data: HiveData = HiveData()
hive_data.set_id_beehive(1)
hive_data.set_hive_bezeichnung("testBezeichnung")

hive_data.set_humidity_in(25)
hive_data.set_humidity_out(30)

hive_data.set_temp_in(10)
hive_data.set_temp_out(20)
hive_data.set_sored_at(curr_time)
hive_data.set_sent_at(curr_time)
hive_data.set_weight(23)

#needs to be changed in DB first
RestClient.put_sensor_data(hive_data, "myToken")


print(curr_time)
