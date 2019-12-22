import tkinter as tk
import RPi.GPIO as GPIO
import Adafruit_DHT as dht
from tkinter import Button, Frame, LEFT, ACTIVE
from tkinter.ttk import Label, Entry, Progressbar

from at.tama.beechecker.beedialog import BeeDialog
from at.tama.beechecker.configuration.hive import Hive
from at.tama.beechecker.configuration.hx711 import HX711

from at.tama.beechecker.configuration.hive_calibration import HiveCalibration
from at.tama.beechecker.dbaccess import DbAccess


def clean():
    print ("Cleaning...")
    GPIO.cleanup()
    print ("Cleaned!")


class CalibrationDialog (BeeDialog):

    _main_window = None #: tk.Tk
    _hive = None #: Hive
    _bar = None #: Progressbar
    _close_enabled = True

    _button_box = None #: Frame
    _start_button = None

    _calibration = None

    _humidity = None
    
    _yes_button = None
    _no_button = None

    _header = None

    _expected_weight_label = None #: : tk.Label
    _expected_weight_field = None #: : tk.Entry
    _expected_weight_box = None

    _weight_display = None
    _temp_display = None

    def __init__(self, main_window: tk.Tk, hive: Hive):
        self._main_window = main_window
        self._hive = hive
        super().__init__(parent=main_window, title="Waage kalibrieren", width=310, height=120)

    def _init_expected_weight_box(self):
        self._expected_weight_box = Frame(self)
        
        self._expected_weight_label = Label(self._expected_weight_box,
                                            text='Gewicht (g)',
                                            font=('Arial', 10),
                                            anchor='e',
                                            wraplength=100,
                                            background='#ffffcc')
        self._expected_weight_label.grid(column=0, row=0, sticky='e')
        self._expected_weight_field = Entry(self._expected_weight_box,
                                            font=('Arial', 8),
                                            width="20")
        self._expected_weight_field.grid(column=1, row=0)

    def open(self):
        pass
    
    def cancel(self, event=None):
        if self._close_enabled:
            super().cancel(event)
        
    def body(self, master):
        self._calibration = HiveCalibration()
        self._header = Label(master, text="")
        self._bar = Progressbar(master, length=210)
        self._init_expected_weight_box()
        self._weight_display = Label(master, text="")
        self._temp_display = Label(master, text="")
        self._prepare_tara()
        
    def _prepare_tara(self):
        self._header.config(text='Drücken Sie "Start" um die Waage\n zu tarieren.')
        self._header.pack()

    def _standard_buttons(self):
        self._button_box = Frame(self)
        self._button_box.pack()
        self._start_button = Button(self._button_box, text="Start", width=10, command=self._calc_offset, default=ACTIVE)
        self._start_button.pack(side=LEFT, padx=5, pady=5)
        w = Button(self._button_box, text="Abbrechen", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

    def _yes_no_buttons(self):
        self._yes_no_button_box = Frame(self)

        self._yes_button = Button(self._yes_no_button_box, text="Ja", width=10, command=self._satisfied, default=ACTIVE)
        self._yes_button.pack(side=LEFT, padx=5, pady=5)
        self._no_button = Button(self._yes_no_button_box, text="Nein", width=10, command=self._not_satisfied)
        self._no_button .pack(side=LEFT, padx=5, pady=5)

    def init_calc_offset(self):
        pass

    def _satisfied(self):
        DbAccess.update_hive_calibration(self._calibration)
        self._close_enabled = True
        self.cancel()

    def _not_satisfied(self):
        self._start_button.config(command=self._calc_offset)
        self._calibration = HiveCalibration()
        self._yes_no_button_box.pack_forget()
        self._temp_display.pack_forget()
        self._weight_display.pack_forget()
        self._prepare_tara()
        self._button_box.pack()
        self.update_idletasks()

    def buttonbox(self):
        self._standard_buttons()
        self._yes_no_buttons()
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        
        '''
        w = Button(box, text="OK", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        '''

    def _progress(self, i, maximum=15):
        self._bar['value']=int(210/(maximum-i))
        self.update_idletasks()

    def _calc_reference_unit(self, event=None):
        expected_weight_string = self._expected_weight_field.get()
        print('calc-reference-unit.expected_weight_string: ', expected_weight_string)
        expected = int(expected_weight_string)
        print('calc-reference-unit.expected: ', expected)
        self._calibration.entity_id = self._hive.get_id()
        self._humidity = None
        self._bar['value'] = 0
        self._bar.pack()
        self.update_idletasks()
        try:
            self._close_enabled = False
            self._button_box.pack_forget()
            self._close_enabled = False
            self._bar.pack()
            self.update_idletasks()

            pins = self._hive.get_weight().get_bcm().split(",")
            data_pin = pins[0]
            clk_pin = pins[1]

            print('data_pin ' + data_pin)
            print('clk_pin ' + clk_pin)
            
            hx = HX711(int(data_pin),int(clk_pin), gain=128)
            hx.set_reading_format("LSB", "MSB")
            print('_offset:', self._calibration.offset)
            hx.set_offset(self._calibration.offset)
            self._calibration.value_per_gram = hx.calc_reference_unit(lambda i: self._progress(i, 10), expected)
            print('reference_unit -> ', self._calibration.value_per_gram)
            self._calc_temp()
            clean()
            self._start_button.config(command=self._check_weight)
            self._header.config(text='Drücken Sie Start um das Gewicht\nzu überprüfen.')
            self._button_box.pack()
            self._bar.pack_forget()
            self._expected_weight_box.pack_forget()
            self._weight_display.pack()
            self._temp_display.pack()
            self.update_idletasks()
            self._close_enabled = True
        except Exception as e:
            print('Error ', e)
            clean()
            self._calibration.offset = None
            self._close_enabled = True

    def _calc_temp(self):
        temp_sensor = self._hive.get_temperature_outside()
        
        if temp_sensor.get_bcm() == '' or temp_sensor.get_product() == '':
            return
        
        if temp_sensor.get_product() == 'DHT22':
            self._humidity, self._calibration.temp = dht.read_retry(dht.DHT22, int(temp_sensor.get_bcm()))
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(self._calibration.temp, self._humidity))
        elif temp_sensor.get_product() == 'DHT11':
            self._humidity, self._temp = dht.read_retry(dht.DHT11, int(temp_sensor.get_bcm()))
            print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(self._calibration.temp, self._humidity))
        else:
            print('Unsupported product ', temp_sensor.get_product())
        

    def _check_weight(self):
        try:
            self._close_enabled = False
            pins = self._hive.get_weight().get_bcm().split(",")
            data_pin = pins[0]
            clk_pin = pins[1]
            hx = HX711(int(data_pin),int(clk_pin), gain=128)
            hx.set_reading_format("LSB", "MSB")
            print('_reference_unit:', self._calibration.value_per_gram)
            hx.set_reference_unit(self._calibration.value_per_gram)
            hx.reset()
            print('_offset:', self._calibration.offset)
            hx.set_offset(self._calibration.offset)
            val = hx.get_weight(5)
            print('value -> ', val)
            self._header.config(text='Sind Sie mit dem Ergebnis\nzufrieden?')
            self._weight_display.config(text=('Gewicht: {0:0.1f}g'.format(val)))
            if self._calibration.temp is not None:
                self._temp_display.config(text=('Temp: {0:0.1f}°C'.format(self._calibration.temp)))
            else:
                self._temp_display.config(text='')
        
            print('reference_unit -> ', self._calibration.value_per_gram)
            clean()
            self._button_box.pack_forget()
            self._yes_no_button_box.pack()
            self.update_idletasks()
            self._close_enabled = True
        except Exception as e:
            print('Error ', e)
            clean()
            self._calibration.offset = None
            self._close_enabled = True
        
    def _calc_offset(self, event=None):
        self._calibration.offset = None
        try:
            self._button_box.pack_forget()
            self._close_enabled = False
            self._bar.pack()
            self.update_idletasks()

            pins = self._hive.get_weight().get_bcm().split(",")
            data_pin = pins[0]
            clk_pin = pins[1]

            print('data_pin ' + data_pin)
            print('clk_pin ' + clk_pin)

            hx = HX711(int(data_pin),int(clk_pin), gain=128)
            hx.set_reading_format("LSB", "MSB")
            self._calibration.offset = hx.calc_offset(lambda i: self._progress(i))
            print('offset -> ', self._calibration.offset)
            clean()
            self._start_button.config(command=self._calc_reference_unit)
            self._header.config(text='Geben Sie ein Gewicht auf die Waage.')
            self._expected_weight_box.pack()
            self._button_box.pack()
            self._bar.pack_forget()
           
            self.update_idletasks()
        except Exception as e:
            print('Fehler', e)
            clean()
            self._close_enabled = True
            self._calibration.offset = None
            
