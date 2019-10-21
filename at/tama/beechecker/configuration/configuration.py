import sys
print(sys.path)
sys.path.append('/home/pi/beechecker')
#sys.path.append('/home/pi/beespy')

from at.tama.beespy.dbaccess import DbAccess
from at.tama.beespy.configuration.main_handler import MainHandler

DbAccess.prepare_db()
mainHandler: MainHandler = MainHandler()
mainHandler.start()
