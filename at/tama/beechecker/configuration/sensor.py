class Sensor:
    _bcm = None
    _product = None

    def __init__(self):
        self._bcm = ''
        self._product = ''

    def set_bcm(self, val):
        self._bcm = val

    def get_bcm(self):
        return self._bcm

    def set_product(self, val):
        self._product = val

    def get_product(self):
        return self._product


