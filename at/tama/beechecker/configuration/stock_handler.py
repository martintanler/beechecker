import tkinter as tk
from tkinter import Entry, Button, StringVar
from tkinter.ttk import Label, Combobox

from at.tama.beechecker.configuration.calibration_dialog import CalibrationDialog
from at.tama.beechecker.dbaccess import DbAccess
from at.tama.beechecker.configuration.hive import Hive
from at.tama.beechecker.configuration.sensor_typ import SUPPORTED_TEMP_PRODS, SUPPORTED_HUMID_PRODS, SUPPORTED_WEIGHT_PRODS


class StockHandler:
    _mainWindow = None #: tk.Tk
    _frame = None #: tk.LabelFrame

    def __init__(self, main_window: tk.Tk):
        self._mainWindow = main_window
        self._frame = tk.LabelFrame(self._mainWindow, borderwidth=5, text='Bienenstöcke / GPIO-BCM', relief='groove', padx=10,
                                    pady=10, background='#ffffcc')

    def open(self):
        for widget in self._frame.winfo_children():
            widget.destroy()
        tk.Frame(self._frame, height=30).grid(row=1)
        self._add_new_hive_component(0)

        headers = ['\n                      Stock-Name', ' GPIO-BCM\n Temp. Innen', ' GPIO-BCM\n Temp. Außen', " GPIO-BCM\n Feucht. Innen", " GPIO-BCM \nFeucht. Außen", "   Data,CLK \n   Gewicht"]
        self._append_headers(headers, headers_row=3)

        for hive in DbAccess.find_hives():
            self._add_to_frame(hive)

        self._frame.pack(pady=40)

    def _append_headers(self, headers, headers_row):
        for index in range(len(headers)):
            w = 12
            if index == 0:
                w = 30
            label = Label(self._frame, text=headers[index], width=w, relief='raised', font=('Arial', 12, 'bold'),
                          justify='center')
            label.grid(row=headers_row, column=index, padx=2)

    def _add_new_hive_component(self, i):
        container = tk.Frame(self._frame, background='#ffffcc')
        add_entry_txt = StringVar()
        add_entry = Entry(container, font=('Arial', 12), width="50", textvariable=add_entry_txt)
        add_button = Button(container, text="Stock anlegen", background="#ccffff", width="15",
                                    command=lambda: self._add_hive(add_entry_txt))
        add_entry.grid(row=i, column=1)
        add_button.grid(row=i, column=2, padx=10)
        container.grid(row=i, columnspan=5)

    def _create_bcm_entry(self, r, col, str_var, parent, entry_width=12, product_values=None, product_txt=None,
                          change_function=None):
        container = tk.Frame(parent, background='#ffffcc')
        entry = Entry(container, font=('Arial', 12), width=entry_width, textvariable=str_var)
        entry.grid(row=0, column=0, pady=2)
        if product_values is not None:
            select_product = Combobox(container, values=product_values, width=entry_width-2, font=('Arial', 12),
                                      state='readonly', textvariable=product_txt)
            select_product.grid(row=1, column=0, pady=2)
            select_product.bind("<<ComboboxSelected>>", change_function)
        container.grid(row=r, column=col, pady=5, padx=2)
        return container

    def _add_to_frame(self, hive: Hive):
        i = len(self._frame.winfo_children()) + 1

        name_txt = StringVar(value=hive.get_name())
        temp_in_txt = StringVar(value=hive.get_temperature_inside().get_bcm())
        temp_in_prd_txt = StringVar(value=hive.get_temperature_inside().get_product())
        temp_out_txt = StringVar(value=hive.get_temperature_outside().get_bcm())
        temp_out_prd_txt = StringVar(value=hive.get_temperature_outside().get_product())
        hum_in_txt = StringVar(value=hive.get_humidity_inside().get_bcm())
        hum_in_prd_txt = StringVar(value=hive.get_humidity_inside().get_product())
        hum_out_txt = StringVar(value=hive.get_humidity_outside().get_bcm())
        hum_out_prd_txt = StringVar(value=hive.get_humidity_outside().get_product())
        weight_txt = StringVar(value=hive.get_weight().get_bcm())
        weight_prd_txt = StringVar(value=hive.get_weight().get_product())

        row_buttons_container = tk.Frame(self._frame, background='#ffffcc')
        row_buttons_container.grid(row=i, column=6, padx=5)

        delete_button = Button(row_buttons_container, text="Löschen", background="#ccffff", width="15",
                               command=lambda: self._delete_hive(hive, row_buttons_container, widgets))
        calibrate_button = Button(row_buttons_container, text="Waage kalibrierren", background="#ccffff", width="15",
                                  command=lambda: self._open_calibration_dialog(hive))

        update_button = Button(self._frame, text="Speichern", background="#ccffff", width="15",
                               command=lambda: self._update_hive(hive, name_txt.get().strip(),
                                                                 temp_in_txt.get().strip(), temp_in_prd_txt.get().strip(),
                                                                 temp_out_txt.get().strip(), temp_out_prd_txt.get().strip(),
                                                                 hum_in_txt.get().strip(), hum_in_prd_txt.get().strip(),
                                                                 hum_out_txt.get().strip(), hum_out_prd_txt.get().strip(),
                                                                 weight_txt.get().strip(), weight_prd_txt.get().strip(),
                                                                 update_button, delete_button, calibrate_button, i))
        change_function = lambda a: self._hive_val_changed(hive, update_button, delete_button, i)

        widgets = [self._create_bcm_entry(i, 0, name_txt, self._frame, entry_width=30),
                   self._create_bcm_entry(i, 1, temp_in_txt, self._frame, product_values=SUPPORTED_TEMP_PRODS,
                                          product_txt=temp_in_prd_txt, change_function=change_function),
                   self._create_bcm_entry(i, 2, temp_out_txt, self._frame, product_values=SUPPORTED_TEMP_PRODS,
                                          product_txt=temp_out_prd_txt, change_function=change_function),
                   self._create_bcm_entry(i, 3, hum_in_txt, self._frame, product_values=SUPPORTED_HUMID_PRODS,
                                          product_txt=hum_in_prd_txt, change_function=change_function),
                   self._create_bcm_entry(i, 4, hum_out_txt, self._frame, product_values=SUPPORTED_HUMID_PRODS,
                                          product_txt=hum_out_prd_txt, change_function=change_function),
                   self._create_bcm_entry(i, 5, weight_txt, self._frame, product_values=SUPPORTED_WEIGHT_PRODS,
                                          product_txt=weight_prd_txt, change_function=change_function)]

        widgets.append(update_button)

        name_txt.trace('w', lambda a, b, c: self._hive_val_changed(hive, update_button, delete_button, i))
        temp_in_txt.trace('w', lambda a, b, c: self._hive_val_changed(hive, update_button, delete_button, i))
        temp_out_txt.trace('w', lambda a, b, c: self._hive_val_changed(hive, update_button, delete_button, i))
        hum_in_txt.trace('w', lambda a, b, c: self._hive_val_changed(hive, update_button, delete_button, i))
        hum_out_txt.trace('w', lambda a, b, c: self._hive_val_changed(hive, update_button, delete_button, i))
        weight_txt.trace('w', lambda a, b, c: self._hive_val_changed(hive, update_button, delete_button, i))

        delete_button.grid(row=0, column=0, padx=5)
        calibrate_button.grid(row=1, column=0, padx=5, pady=2)

    def _hive_val_changed(self, hive: Hive, update_button: Button, delete_button: Button, row_num):
        delete_button.grid_remove()
        update_button.grid(row=row_num, column=6)

    def _update_hive(self, hive: Hive, name: str,
                     temp_in, temp_in_prod,
                     temp_out, temp_out_prod,
                     hum_in, hum_in_prod,
                     hum_out, hum_out_prod,
                     weight,  weight_prod,
                     update_button: Button,
                     delete_button: Button,
                     calibrate_button: Button,
                     row_num):
        hive.set_name(name)
        hive.get_temperature_inside().set_bcm(temp_in)
        hive.get_temperature_inside().set_product(temp_in_prod)
        hive.get_temperature_outside().set_bcm(temp_out)
        hive.get_temperature_outside().set_product(temp_out_prod)
        hive.get_humidity_inside().set_bcm(hum_in)
        hive.get_humidity_inside().set_product(hum_in_prod)
        hive.get_humidity_outside().set_bcm(hum_out)
        hive.get_humidity_outside().set_product(hum_out_prod)
        hive.get_weight().set_bcm(weight)
        hive.get_weight().set_product(weight_prod)
        DbAccess.update_hive(hive)
        update_button.grid_remove()
        #delete_button.grid(row=row_num, column=6)
        #calibrate_button.grid(row=row_num, column=6)
        delete_button.grid(row=0, column=0, padx=5)
        calibrate_button.grid(row=1, column=0, padx=5, pady=2)

    def _delete_hive(self, hive: Hive, row_buttons_container, widgets):
        DbAccess.delete_hive(hive)
        row_buttons_container.destroy()
        for widget in widgets:
            widget.destroy()

    def _add_hive(self, svar: StringVar):
        hive = DbAccess.add_hive(svar.get())
        self._add_to_frame(hive)
        svar.set('')

    def _edit_hive(self, hive: Hive):
        print(hive)

    def _open_calibration_dialog(self, hive: Hive):
        handler = CalibrationDialog(self._mainWindow, hive)

