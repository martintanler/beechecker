import sqlite3

import array as arr

from at.tama.beechecker.configuration.hive import Hive
from at.tama.beechecker.configuration.hive_calibration import HiveCalibration
from at.tama.beechecker.configuration.imker import BeeKeeper
from at.tama.beechecker.configuration.sensor import Sensor
from at.tama.beechecker.configuration.sensor_typ import TEMP_IN, TEMP_OUT, HUMIDITY_IN, HUMIDITY_OUT, WEIGHT
from at.tama.beechecker.sensor.hivedata import HiveData


class DbAccess:

    @staticmethod
    def _db_connect():
        return sqlite3.connect('sensordata.db')

    @staticmethod
    def _commit_and_close(conn):
        # Save (commit) the changes
        conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        conn.close()

    @staticmethod
    def prepare_db():

        conn = DbAccess._db_connect()

        c = conn.cursor()

        # Create table beekeeper
        c.execute('''CREATE TABLE if not exists beekeeper(id INTEGER PRIMARY KEY AUTOINCREMENT,  
                        mail TEXT not null unique,
                        token TEXT not null
                    )
        ''')

        # Create table beehive
        c.execute('''CREATE TABLE if not exists beehive(id INTEGER PRIMARY KEY AUTOINCREMENT,  
                        bezeichnung TEXT not null unique,
                        offsetvalue NUMERIC,
                        kalib_gramm NUMERIC,
                        kalib_val_pro_gramm NUMERIC,
                        kalib_temp NUMERIC
                    )
        ''')

        # Create table sensor
        c.execute('''CREATE TABLE if not exists sensor(id INTEGER PRIMARY KEY AUTOINCREMENT,  
                        gpio TEXT,
                        typ TEXT,
                        product,
                        idbeehive INTEGER not null,
                        CONSTRAINT UK_SENSOR_01 UNIQUE (gpio, typ, product),
                        FOREIGN KEY (idbeehive) REFERENCES beehive (id)
                        ON DELETE CASCADE ON UPDATE NO ACTION
                    )
        ''')

        # Create sensordata table
        c.execute('''CREATE TABLE if not exists sensordata(id INTEGER PRIMARY KEY AUTOINCREMENT,
                        idbeehive INTEGER not null,  
                        temp_in NUMERIC,
                        temp_out NUMERIC, 
                        humidity_in NUMERIC,  
                        humidity_out NUMERIC, 
                        weight NUMERIC,
                        stored DATETIME not null, 
                        sent_to_server DATETIME, 
                        CONSTRAINT UK_SENSORDATA_01 UNIQUE (idbeehive, stored),
                        FOREIGN KEY(idbeehive) REFERENCES beehive(id)
                    )
        ''')
        DbAccess._commit_and_close(conn)

    @staticmethod
    def find_beekeeper() -> BeeKeeper:
        conn = DbAccess._db_connect()
        c = conn.cursor()
        c.execute("SELECT mail, token FROM beekeeper")
        row = c.fetchone()
        DbAccess._commit_and_close(conn)
        if row is not None:
            return BeeKeeper(row[0], row[1])

    @staticmethod
    def persist_token(mail: str, token: str):
        conn = DbAccess._db_connect()
        c = conn.cursor()
        # Update beekeepers token
        c.execute('''INSERT OR REPLACE  into beekeeper (mail, token) values (?,?)
               ''', (mail, token))

        DbAccess._commit_and_close(conn)

    @staticmethod
    def persist_hive_data(hive_data: HiveData):
        conn = DbAccess._db_connect()
        c = conn.cursor()
        # Update beekeepers token
        c.execute('''INSERT OR REPLACE  into sensordata ( idbeehive, temp_in, temp_out, humidity_in, humidity_out, weight, stored, sent_to_server ) values (?,?,?,?,?,?,?,?)
               ''', (
        hive_data.get_id_beehive(), hive_data.get_temp_in(), hive_data.get_temp_out(), hive_data.get_humidity_in(),
        hive_data.get_humidity_out(), hive_data.get_weight(), hive_data.get_stored_at(), hive_data.get_sent_at()))

        DbAccess._commit_and_close(conn)

    @staticmethod
    def find_hives() -> []:
        hives = []
        conn = DbAccess._db_connect()
        c = conn.cursor()
        for row in c.execute("SELECT id, bezeichnung, kalib_val_pro_gramm FROM beehive"):
            print(row[0])
            print(row[1])
            hive = Hive(row[0], row[1])
            hive.set_calibrated(row[2] is not None)
            DbAccess._append_sensors(hive)
            hives.append(hive)
        DbAccess._commit_and_close(conn)
        return hives

    @staticmethod
    def find_hive(name: str) -> []:
        conn = DbAccess._db_connect()
        c = conn.cursor()
        c.execute("SELECT id, bezeichnung, kalib_val_pro_gramm FROM beehive where bezeichnung=?", [name])
        row = c.fetchone()
        hive = Hive(row[0], row[1])
        hive.set_calibrated(row[2] is not None)
        DbAccess._append_sensors(hive)
        DbAccess._commit_and_close(conn)
        return hive

    @staticmethod
    def _append_sensors(hive: Hive):
        conn = DbAccess._db_connect()
        c = conn.cursor()
        print('hive.id: ', hive.get_id())
        for row in c.execute("SELECT gpio, typ, product FROM sensor where idbeehive=?", [hive.get_id()]):
            print(row)
            sensor = Sensor()
            sensor.set_bcm(row[0])
            sensor.set_product(row[2])
            if row[1] == TEMP_IN:
                hive.set_temperature_inside(sensor)
            elif row[1] == TEMP_OUT:
                hive.set_temperature_outside(sensor)
            elif row[1] == HUMIDITY_IN:
                hive.set_humidity_inside(sensor)
            elif row[1] == HUMIDITY_OUT:
                hive.set_humidity_outside(sensor)
            elif row[1] == WEIGHT:
                hive.set_weight(sensor)
        DbAccess._commit_and_close(conn)

    @staticmethod
    def delete_hive(hive: Hive):
        conn = DbAccess._db_connect()
        c = conn.cursor()
        c.execute('''delete from sensor where idbeehive=?''', [hive.get_id()])
        c.execute('''delete from  beehive where id=?''', [hive.get_id()])
        DbAccess._commit_and_close(conn)

    @staticmethod
    def update_hive(hive: Hive):
        conn = DbAccess._db_connect()
        c = conn.cursor()
        c.execute('''update beehive set bezeichnung=? where id=?''', [hive.get_name(), hive.get_id()])
        c.execute('''delete from sensor where idbeehive=?''', [hive.get_id()])
        sensors = [[TEMP_IN, hive.get_temperature_inside()],
                   [TEMP_OUT, hive.get_temperature_outside()],
                   [HUMIDITY_IN, hive.get_humidity_inside()],
                   [HUMIDITY_OUT, hive.get_humidity_outside()],
                   [WEIGHT, hive.get_weight()]
                   ]
        for sensor in sensors:
            if sensor[1] is not None:
                c.execute('''INSERT into sensor (idbeehive, typ, gpio, product) values (?, ?, ?, ?)''',
                          [hive.get_id(), sensor[0], sensor[1].get_bcm().strip(), sensor[1].get_product().strip()])

        DbAccess._commit_and_close(conn)

    @staticmethod
    def update_hive_calibration(hive_calibration: HiveCalibration):
        conn = DbAccess._db_connect()
        c = conn.cursor()

        c.execute('''update beehive set offsetvalue=?, kalib_gramm=?, kalib_val_pro_gramm=?, kalib_temp=? where id=?''',
                  [hive_calibration.offset, hive_calibration.weight, hive_calibration.value_per_gram,
                   hive_calibration.temp, hive_calibration.entity_id])

        DbAccess._commit_and_close(conn)

    @staticmethod
    def find_hive_calibration(name: str) -> []:
        conn = DbAccess._db_connect()
        c = conn.cursor()
        c.execute("SELECT offsetvalue, kalib_gramm, kalib_val_pro_gramm, kalib_temp FROM beehive where bezeichnung=?",
                  [name])
        row = c.fetchone()
        hive_calibration = HiveCalibration()
        hive_calibration.offset = row[0]
        hive_calibration.weight = row[1]
        hive_calibration.value_per_gram = row[2]
        hive_calibration.temp = row[3]
        DbAccess._commit_and_close(conn)
        return hive_calibration

    @staticmethod
    def add_hive(name: str):
        conn = DbAccess._db_connect()
        c = conn.cursor()
        c.execute('''INSERT into beehive (bezeichnung) values (?)''', [name])
        DbAccess._commit_and_close(conn)
        return DbAccess.find_hive(name)
