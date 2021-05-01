from .SimulationObject import *

from model.objects.StatModel import *

class Stat( SimulationObject ):

	def __init__( self, simulation, type ):
		super( ).__init__( 'model.objects.StatModel', 'StatModel', simulation )

		self.set_type( type )

	def get_type( self ):
		model = self.get_model( )
		return model.get_type( )

	def set_type( self, new_type ):
		model = self.get_model( )
		model.set_type( new_type )

	def get_data( self ):
		model = self.get_model( )
		return model.get_data( )

	def set_data( self, data ):
		model = self.get_model( )
		model.set_data( data )