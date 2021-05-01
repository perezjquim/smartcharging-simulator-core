from base.BaseModel import *

class SimulationModel( BaseModel ):

	class sqlmeta:
		table = 'Simulations'	

	_description = StringCol( default = '', dbName = 'description', title = 'description' )
	_cars = MultipleJoin( 'CarModel' )
	_charging_plugs = MultipleJoin( 'PlugModel' )
	_logs = MultipleJoin( 'LogModel' )

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