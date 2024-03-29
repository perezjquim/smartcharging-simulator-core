from .SimulationObjectModel import *

class LogModel( SimulationObjectModel ):

	csvFilename = 'Logs'
	class sqlmeta:
		table = 'Logs'
	
	_message = StringCol( default = '', dbName = 'message', title = 'message' )

	def get_message( self ):
		return self._message

	def set_message( self, message ):
		self._message = message