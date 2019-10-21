from at.tama.beechecker.configuration.hive_calibration import HiveCalibration
from at.tama.beechecker.configuration.sensor import Sensor


class Hive:
    #int
    _entity_id = 0
    #str
    _name = ''
    _temperature_outside = Sensor()
    _temperature_inside = Sensor()
    _humidity_outside = Sensor()
    _humidity_inside = Sensor()
    _weight = Sensor()
    _calibrated = False

    def __init__(self, entity_id: int, name: str):
        self._entity_id = entity_id
        self._name = name

    def set_name(self, val: str):
        self._name = val

    def get_name(self):
        return self._name

    def set_temperature_outside(self, val: Sensor):
        self._temperature_outside = val

    def get_temperature_outside(self):
        return self._temperature_outside

    def set_temperature_inside(self, val: Sensor):
        self._temperature_inside = val

    def get_temperature_inside(self):
        return self._temperature_inside

    def set_humidity_outside(self, val: Sensor):
        self._humidity_outside = val

    def get_humidity_outside(self):
        return self._humidity_outside

    def set_humidity_inside(self, val: Sensor):
        self._humidity_inside = val

    def get_humidity_inside(self):
        return self._humidity_inside

    def set_weight(self, val: Sensor):
        self._weight = val

    def get_weight(self):
        return self._weight

    def set_calibrated(self, val: bool):
        self._calibrated = val

    def get_calibrated(self):
        return self._calibrated

    def get_id(self):
        return self._entity_id

