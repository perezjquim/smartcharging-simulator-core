from sqlobject import *

from core.constants.CarConstants import *	
from .SimulationObjectModel import *	

class CarModel( SimulationObjectModel ):

	class sqlmeta:
		table = 'Cars'

	_status = StringCol( default = CarConstants.STATUS_READY, dbName = 'status' )
	_travels = MultipleJoin( 'TravelModel' )
	_charging_periods = MultipleJoin( 'ChargingPeriodModel' )
	_battery_level = FloatCol( default = CarConstants.DEFAULT_BATTERY_LEVEL, dbName = 'battery_level' )
	_plug = ForeignKey( 'PlugModel', default = None, dbName = 'plug_id' )

	def get_status( self ):
		return self._status

	def set_status( self, new_status ):
		self._status = new_status

	def get_travels( self ):
		return self._travels

	def add_travel( self, new_travel ):
		self._travels.append( new_travel )

	def get_charging_periods( self ):
		return self._charging_periods

	def add_charging_period( self, new_charging_period ):
		self._charging_periods.append( new_charging_period )

	def get_battery_level( self ):
		return self._battery_level

	def set_battery_level( self, battery_level ):
		if battery_level >= 0 and battery_level <= 10:
			self._battery_level = battery_level
		elif battery_level < 0:
			self._battery_level = 0
		elif battery_level > 10:
			self._battery_level = 10
		else:
			self.log( 'Invalid battery level given!' )

	def get_plug( self ):
		return self._plug			

	def set_plug( self, new_plug ):
		self._plug = new_plug