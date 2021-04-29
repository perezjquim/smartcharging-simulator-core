from .SimulationObject import *

from model.objects.LogModel import *

class Log( SimulationObject ):

	def __init__( self, simulation, message ):
		super( ).__init__( 'model.objects.LogModel', 'LogModel', simulation )

		self.set_message( message )

	def get_message( self ):
		model = self.get_model( )
		return model.get_message( )

	def set_message( self, message ):
		model = self.get_model( )
		model.set_message( message )