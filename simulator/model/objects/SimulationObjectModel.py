from base.BaseModel import *

class SimulationObjectModel( BaseModel ):
	
	_simulation = ForeignKey( 'SimulationModel', default = None, dbName = 'simulation_id' )

	def get_simulation( self ):
		return self._simulation

	def set_simulation( self, simulation ):
		self._simulation = simulation