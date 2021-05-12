from .SimulationObject import *

from model.objects.LogModel import *

class Log( SimulationObject ):

	def __init__( self, simulation = None, message = '', model_instance = None ):
		super( ).__init__( 'model.objects.LogModel', 'LogModel', model_instance, simulation )

		if message:
			self.set_message( message )

	def get_message( self ):
		model = self.get_model( )
		return model.get_message( )

	def set_message( self, message ):
		if not self.is_read_only( ):		
			model = self.get_model( )
			model.set_message( message )

	def get_data( self ):
		data = super( ).get_data( )

		data.update({
			'message' : self.get_message( )
		})

		return data