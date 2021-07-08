from core.constants.PlugConstants import *
from .SimulationObjectModel import *
	
class PlugModel( SimulationObjectModel ):

	csvFilename = 'Plugs'
	class sqlmeta:
		table = 'Plugs'	

	_status = StringCol( default = PlugConstants.STATUS_ENABLED, dbName = 'status', title = 'status' )	
	_plugged_car = ForeignKey( 'CarModel', default = None, dbName = 'car_id', title = 'car_id' )
	_energy_consumption = FloatCol( default = 0, dbName = 'energy_consumption', title = 'energy_consumption' )
	_charging_periods = MultipleJoin( 'ChargingPeriodModel', joinColumn = 'plug_id' )

	def get_status( self ):
		return self._status

	def set_status( self, new_status ):
		self._status = new_status

	def get_plugged_car( self ):
		return self._plugged_car

	def set_plugged_car( self, car ):
		self._plugged_car = car

	def get_energy_consumption( self ):
		return round( self._energy_consumption, 2 )

	def set_energy_consumption( self, new_energy_consumption ):
		self._energy_consumption = round( new_energy_consumption, 2 )

	def get_charging_periods( self ):
		return self._charging_periods			

	def add_charging_period( self, new_charging_period ):
		self._charging_periods.append( new_charging_period )		