from . import *
import time
import importlib

class Simulator:

	DEBUG_MODE = True

	def __init__( self ):
		self._cars = []		
		self._chargingAlgorithm = None
		self._config = None
		self._dataModels = {}	
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

		if Simulator.DEBUG_MODE == True:
			print( '>>> Config' )
			print( self._config )	
			print( '<<< Config\n' )

		print( "Fetching config... done!" )

	def fetchDataModels( self ):
		print( "Fetching data models..." )

		module = importlib.import_module( 'models' )
		classes = module.__dict__.items( )

		exclude_classes = [ 'IDataModel' ]
		classes = dict( [ 
			(name, c) for (name, c) in classes 
				if not ( name.startswith( '__' ) ) 
				and name not in exclude_classes 
		] ).items( )

		for name, c in classes:
			self._dataModels[ name ] = c( )

		if Simulator.DEBUG_MODE == True:
			print( '>>> Data models' )
			print( self._dataModels )
			print( '<<< Data models\n' )		

		print( "Fetching data models... done!" )

	def getChargingAlgorithm( self ):
		return self._chargingAlgorithm

	def setChargingAlgorithm( self, chargingAlgorithmName ):
		module = __import__( "algorithms" )
		chargingAlgorithm = getattr( module, chargingAlgorithmName ) 
		self._chargingAlgorithm = chargingAlgorithm
