from sqlobject import *

from core.constants.PlugConstants import *
from .SimulationObjectModel import *
	
class PlugModel( SimulationObjectModel ):

	class sqlmeta:
		table = 'Plugs'	

	_status = StringCol( default = PlugConstants.STATUS_ENABLED, dbName = 'status' )	
	_plugged_car = ForeignKey( 'CarModel', default = None, dbName = 'car_id' )
	_energy_consumption = FloatCol( default = 0, dbName = 'energy_consumption' )
	_charging_periods = MultipleJoin( 'ChargingPeriodModel' )

	def get_status( self ):
		return self._status

	def set_status( self, new_status ):
		self._status = new_status

	def plug_car( self, car ):
		if self.is_enabled( ):
			self._plugged_car = car

	def unplug_car( self ):
		car = self.get_plugged_car( )
		car.set_plug( None )
		self._plugged_car = None

	def get_plugged_car( self ):
		return self._plugged_car

	def get_energy_consumption( self ):
		return self._energy_consumption

	def set_energy_consumption( self, new_energy_consumption ):
		if self.is_enabled( ):
			self._energy_consumption = new_energy_consumption	
		else:
			self._energy_consumption = 0

	def get_charging_periods( self ):
		return self._charging_periods			

	def add_charging_period( self, new_charging_period ):
		self._charging_periods.append( new_charging_period )		