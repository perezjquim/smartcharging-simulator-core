from . import *
from data import *
import time
import importlib
import threading

class Simulator:

	DEBUG_MODE = True

	def __init__( self ):
		self._config = None
		#TODO	

	def onInit( self ):
		self.fetchConfig( )

		self._oRunThread = threading.Thread( target = self._run )
		self._oRunThread.start( )

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

	def _run( self ):	
		sim_sampling_rate = self._config[ 'sim_sampling_rate' ]		
		
		while True:
			self.onStep( )
			time.sleep( sim_sampling_rate )
