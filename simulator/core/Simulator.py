from . import *
from data import *
import time
import importlib
import threading
import requests

class Simulator:

	DEBUG_MODE = True
	GATEWAY_REQUEST_BASE = 'http://cont_energysim_gateway:8000/{}'

	def __init__( self ):
		self._config = None
		#TODO	

	def onInit( self ):
		self.fetchConfig( )

		self._oRunThread = threading.Thread( target = self._run )
		self._oRunThread.start( )

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
			time.sleep( sim_sampling_rate / 1000 )		

	def onStep( self ):
		print( "Step example!" )

		affluence = self._fetch_gateway("getAffluence/12")
		print( affluence )

		travel_distance = self._fetch_gateway("getTravelDistance")
		print( travel_distance )

		charging_period_duration = self._fetch_gateway("getChargingPeriodDuration")
		print( charging_period_duration )

		charging_period_peak = self._fetch_gateway("getChargingPeriodPeak")
		print( charging_period_peak )

		final_battery_level = self._fetch_gateway("getFinalBatteryLevel/11/1")
		print( final_battery_level )

		#TODO

	def _fetch_gateway( self, endpoint ):
		response = requests.get(self.GATEWAY_REQUEST_BASE.format(endpoint))
		response_json = response.json()

		return response_json


