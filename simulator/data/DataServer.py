from flask import Blueprint

oAPI = Blueprint( "DataServer", __name__ )

class DataServer:

	def __init__( self, oSimulator ):
		#TODO
		self._oSimulator = oSimulator
		pass

	def run( self ):
		#TODO
		oDataServerAPI.run( )		
		pass

	def getBlueprint( self ):
		return oAPI

	@oAPI.route( '/' )
	def root( ):
		return "test root!"
