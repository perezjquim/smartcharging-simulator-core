from .SimulationObject import *

from model.objects.StatModel import *

class Stat( SimulationObject ):

	def __init__( self, simulation = None, stat_type = '', model_instance = None ):
		super( ).__init__( 'model.objects.StatModel', 'StatModel', model_instance, simulation )

		if stat_type:
			self.set_type( stat_type )

	def get_type( self ):
		model = self.get_model( )
		return model.get_type( )

	def set_type( self, new_type ):
		if not self.is_read_only( ):
			model = self.get_model( )
			model.set_type( new_type )

	def get_data( self ):
		model = self.get_model( )
		return model.get_data( )

	def set_data( self, data ):
		if not self.is_read_only( ):		
			model = self.get_model( )
			model.set_data( data )