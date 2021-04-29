from base.BaseModelProxy import *

class SimulationObject( BaseModelProxy ):

	_simulation = None

	def __init__( self, model_class_path, model_class_name, simulation ):
		super( ).__init__( model_class_path, model_class_name )

		self.set_simulation( simulation )

	def get_simulation( self ):
		return self._simulation

	def set_simulation( self, simulation ):
		self._simulation = simulation
		simulation_model = simulation.get_model( )

		model = self.get_model( )
		model.set_simulation( simulation_model )