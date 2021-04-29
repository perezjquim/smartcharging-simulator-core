from sqlobject import *

from .SimulationObjectModel import *

class LogModel( SimulationObjectModel ):

	class sqlmeta:
		table = 'Logs'
	
	_message = StringCol( default = '', dbName = 'message' )

	def get_message( self ):
		return self._message