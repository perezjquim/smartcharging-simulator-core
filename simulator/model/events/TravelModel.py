from sqlobject import *

from .CarEventModel import *

class TravelModel( CarEventModel ):

	class sqlmeta:
		table = 'Travels'	

	_distance = FloatCol( default = 0, dbName = 'distance' )
	_battery_consumption = FloatCol( default = 0, dbName = 'battery_consumption' )	

	def get_distance( self ):
		return self._distance

	def get_battery_consumption( self ):
		return self._battery_consumption

	def set_distance( self, distance ):
		self._distance = distance

	def set_battery_consumption( self, battery_consumption ):
		self._battery_consumption = battery_consumption