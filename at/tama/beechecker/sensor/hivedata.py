import datetime


class HiveData:

    _id_beehive = None #: int
    _hive_bezeichnung = None #: str

    _temp_in = None #: float
    _temp_out = None #: float
    _humidity_in = None #: float
    _humidity_out = None #: float
    _weight = None #: float

    _stored_at = None #: datetime
    _sent_at = None #: datetime

    def set_id_beehive(self, id_beehive:int):
        self._id_beehive = id_beehive

    def get_id_beehive(self):
        return self._id_beehive

    def set_hive_bezeichnung(self, val: str):
        self._hive_bezeichnung = val

    def get_hive_bezeichnung(self):
        return self._hive_bezeichnung

    def set_temp_in(self, temp_in: float):
        self._temp_in = temp_in

    def get_temp_in(self):
        return self._temp_in

    def set_temp_out(self, temp_out: float):
        self._temp_out = temp_out

    def get_temp_out(self):
        return self._temp_out

    def set_humidity_in(self, humidity_in: float):
        self._humidity_in = humidity_in

    def get_humidity_in(self):
        return self._humidity_in

    def set_humidity_out(self, humidity_out: float):
        self._humidity_out = humidity_out

    def get_humidity_out(self):
        return self._humidity_out

    def set_weight(self, weight: float):
        self._weight = weight

    def get_weight(self):
        return self._weight

    def set_sored_at(self, val: datetime):
        self._stored_at = val

    def get_stored_at(self):
        return self._stored_at

    def set_sent_at(self, val: datetime):
        self._sent_at = val

    def get_sent_at(self):
        return self._sent_at


