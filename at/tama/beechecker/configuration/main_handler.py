import tkinter as tk
from tkinter import Tk

from at.tama.beechecker.dbaccess import DbAccess
from at.tama.beechecker.configuration.imker import BeeKeeper
from at.tama.beechecker.configuration.login_handler import LoginHandler
from at.tama.beechecker.configuration.stock_handler import StockHandler


class MainHandler:
    _window = None#: Tk
    _bk = None #: BeeKeeper
    _loginHandler = None #: LoginHandler
    _stockHandler = None #: StockHandler

    def __init__(self):
        self._window = tk.Tk()
        self._window.geometry("{0}x{1}+0+0".format(
            self._window.winfo_screenwidth() - 3, self._window.winfo_screenheight() - 3))
        self._window.title('BeeSpy - Konfiguration')
        self._loginHandler = LoginHandler(self._window)
        self._stockHandler = StockHandler(self._window)

    def start(self):
        beekeeper = DbAccess.find_beekeeper()
        if beekeeper is None:
            self._loginHandler.open()
            self._loginHandler.add_observer(self.on_bk_found)
            print('Öffne das Fenster um das Service um einen Token zu bitten.')
        else:
            self.on_bk_found(beekeeper)
        self._window.mainloop()

    def on_bk_found(self, bk: BeeKeeper):
        print('on_bk_found')
        self._bk = bk
        self._loginHandler.close()
        self._stockHandler.open()

