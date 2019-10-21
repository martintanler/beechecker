from at.tama.beechecker.dbaccess import DbAccess
from at.tama.beechecker.configuration.main_handler import MainHandler

DbAccess.prepare_db()
mainHandler = MainHandler()
mainHandler.start()
