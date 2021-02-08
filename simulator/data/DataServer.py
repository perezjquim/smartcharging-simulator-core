from flask import Blueprint

api = Blueprint( "DataServer", __name__ )

class DataServer:

	_simulator = None

	def __init__( self, simulator ):
		#TODO
		self._simulator = simulator
		pass

	def run( self ):
		#TODO
		api.run( )		
		pass

	def get_blueprint( self ):
		return api

	@api.route( '/' )
	def root( ):
		return "test root!"
