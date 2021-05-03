from .SimulationObjectModel import *
	
class StatModel( SimulationObjectModel ):

	csvFilename = 'SimulationStats'
	class sqlmeta:
		table = 'SimulationStats'	

	_type = StringCol( default = '', dbName = 'type', title = 'type' )
	_data = JSONCol( default = { }, dbName = 'data', title = 'data' )	

	def get_type( self ):
		return self._type

	def set_type( self, new_type ):
		self._type = new_type

	def get_data( self ):
		return self._data

	def set_data( self, data ):
		self._data = data