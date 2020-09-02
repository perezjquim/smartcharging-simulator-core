from . import *

class Simulator:

	def __init__( self ):
		self._cars = []		
		self._chargingAlgorithm = None
		self._config = None
		self._dataModels = []		

	def onInit( self ):
		self._config = ConfigurationHelper.readConfig( )
		pass

	def onStep( self ):
		pass

	def fetchConfig( self ):
		pass

	def fetchDataModels( self ):
		pass

	def getChargingAlgorithm( self ):
		pass		

	def setChargingAlgorithm( self ):
		pass