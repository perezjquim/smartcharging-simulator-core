from base.BaseModel import *

class SimulationModel( BaseModel ):

	csvFilename = 'Simulations'
	class sqlmeta:
		table = 'Simulations'	

	_description = StringCol( default = '', dbName = 'description', title = 'description' )
	_cars = MultipleJoin( 'CarModel', joinColumn = 'simulation_id' )
	_charging_plugs = MultipleJoin( 'PlugModel', joinColumn = 'simulation_id' )
	_logs = MultipleJoin( 'LogModel', joinColumn = 'simulation_id' )
	_stats = MultipleJoin( 'StatModel', joinColumn = 'simulation_id' )

	def get_description( self ):
		return self._description

	def set_description( self, description ):
		self._description = description

	def get_cars( self ):
		return self._cars

	def add_car( self, new_car ):
		self._cars.append( new_car )

	def get_charging_plugs( self ):
		return self._charging_plugs

	def add_charging_plug( self, new_charging_plug ):
		self._charging_plugs.append( new_charging_plug )

	def get_logs( self ):
		return self._logs

	def get_stats( self ):
		return self._stats