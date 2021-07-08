from .CarEventModel import *

class TravelModel( CarEventModel ):

	csvFilename = 'Travels'
	class sqlmeta:
		table = 'Travels'	

	_distance = FloatCol( default = 0, dbName = 'distance', title = 'distance' )
	_battery_consumption = FloatCol( default = 0, dbName = 'battery_consumption', title = 'battery_consumption' )	

	def get_distance( self ):
		return round( self._distance, 2 )

	def get_battery_consumption( self ):
		return round( self._battery_consumption, 2 )

	def set_distance( self, distance ):
		self._distance = round( distance, 2 )

	def set_battery_consumption( self, battery_consumption ):
		self._battery_consumption = round( battery_consumption, 2 )