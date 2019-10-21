import tkinter as tk
from tkinter import StringVar

#from request import ConnectionError

from at.tama.beechecker.dbaccess import DbAccess
from at.tama.beechecker.restclient import RestClient


class LoginHandler:

    _observers = []

    _mainWindow = None #: tk.Tk
    _frame = None #: : tk.Frame

    _emailLabel = None #: : tk.Label
    _emailField = None #: : tk.Entry

    _pwdLabel = None #: : tk.Label
    _pwdField = None #: : tk.Entry

    _ok = None #: : tk.Button
    _cancel = None #: : tk.Button

    _errorLabel = None #: : tk.Label

    _error = None #: : StringVar

    def __init__(self, main_window: tk.Tk):
        self._mainWindow = main_window
        self._frame = tk.Frame(self._mainWindow, borderwidth=5, relief='groove', padx=10, pady=10, background='#ffffcc')

        self._emailLabel = tk.Label(self._frame, text='E-Mail', font=('Arial', 14), anchor='e', wraplength=100,
                                    padx=10, pady=5, background='#ffffcc')
        self._emailLabel.grid(column=0, row=0, sticky='e')
        self._emailField = tk.Entry(self._frame, font=('Arial', 12), width="20")
        self._emailField.grid(column=1, row=0)

        self._pwdLabel = tk.Label(self._frame, text='Passwort', font=('Arial', 14), anchor='e', wraplength=100,
                                  padx=10, pady=5, background='#ffffcc')
        self._pwdLabel.grid(column=0, row=2, sticky='e')
        self._pwdField = tk.Entry(self._frame, show="*", font=('Arial', 12), width="20")
        self._pwdField.grid(column=1, row=2)

        self._ok = tk.Button(self._frame, text="Anmelden", background="#ccffff", width="15", command=self._on_ok)
        self._ok.grid(column=1, row=3)

        self._error = StringVar()
        self._errorLabel = tk.Label(self._frame,  textvariable=self._error, font=('Arial', 14),
                                    padx=10, pady=5, foreground="#ff0000", background='#ffffcc', wraplength=300)

    def add_observer(self, observer):
        self._observers.append(observer)

    def remove_observer(self, observer):
        self._observers.remove(observer)

    def _on_ok(self):
        self._errorLabel.grid_remove()
        self._frame.update()
        try:
            mail = self._emailField.get()
            token = RestClient.request_token(mail, self._pwdField.get())
            if token is not None:
                DbAccess.persist_token(mail, token)
                bk = DbAccess.find_beekeeper()
                for observer in self._observers:
                    observer(bk)
            else:
                self._error.set('Ups, das ist ein Fehler passiert.')
                self._errorLabel.grid(columnspan=4, row=4)
        except ConnectionError as err:
            print('error: ', err)
            self._error.set('Es konnte keine Verbindung zum Server hergestellt werden.')
            self._errorLabel.grid(columnspan=4, row=4)

    def open(self):
        self._errorLabel.grid_remove()
        self._frame.pack(pady=40)

    def close(self):
        print('close')
        self._frame.pack_forget()
        self._mainWindow.update()
