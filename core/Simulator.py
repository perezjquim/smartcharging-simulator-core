from . import *
import time
import importlib

class Simulator:

	def __init__( self ):
		self._cars = []		
		self._chargingAlgorithm = None
		self._config = None
		self._dataModels = []	
		#TODO	

	def onInit( self ):
		self.fetchConfig( )
		self.fetchDataModels( )

		sim_default_algorithm = self._config[ 'sim_default_algorithm' ]
		self.setChargingAlgorithm( sim_default_algorithm )

		sim_sampling_rate = self._config[ 'sim_sampling_rate' ]

		while True:
			self.onStep( )
			time.sleep( sim_sampling_rate )

	def onStep( self ):
		print( "Step example!" )
		#TODO

	def fetchConfig( self ):
		print( "Fetching config..." )
		
		self._config = ConfigurationHelper.readConfig( )
		print( self._config )	

		print( "Fetching config... done!" )

	def fetchDataModels( self ):
		print( "Fetching data models..." )

		#TODO

		print( "Fetching data models... done!" )

	def getChargingAlgorithm( self ):
		return self._chargingAlgorithm

	def setChargingAlgorithm( self, chargingAlgorithmName ):
		module = __import__( "algorithms" )
		chargingAlgorithm = getattr( module, chargingAlgorithmName ) 
		self._chargingAlgorithm = chargingAlgorithm
