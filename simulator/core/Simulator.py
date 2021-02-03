from . import *
from data import *
import time
import importlib
import threading
import requests

class Simulator:

	DEBUG_MODE = True
	GATEWAY_REQUEST_BASE = 'http://cont_energysim_gateway:8000/{}'

	_run_thread = None	

	_config = [ ]
	_cars = [ ]
	_current_hour_of_day = 0
	_minutes_simulated = 0

	def __init__( self ):
		pass
		#TODO	

	def onInit( self ):
		self.fetchConfig( )

		self._run_thread = threading.Thread( target = self._run )
		self._run_thread.start( )

	def fetchConfig( self ):
		print( "Fetching config..." )
		
		self._config = ConfigurationHelper.readConfig( )

		self._log( '>>> Config' )
		self._log( self._config )	
		self._log( '<<< Config\n' )

		print( "Fetching config... done!" )

	def _log( self, message ):
		if Simulator.DEBUG_MODE == True:
			print( message )

	def _getConfig( self, config_key ):
		return self._config[ config_key ]

	def _run( self ):	
		sim_sampling_rate = self._getConfig( 'sim_sampling_rate' )

		print( 'Initializing cars...' )
		number_of_cars = self._getConfig( 'number_of_cars' )
		for n in range( number_of_cars ):
			self._cars.append( Car( ) )
		print( 'Initializing cars... done!' )

		print( 'Simulating...' )
		number_of_steps = self._getConfig( 'number_of_steps' )
		for n in range( number_of_steps ):
			self.onStep( )
			time.sleep( sim_sampling_rate / 1000 )	
		print( 'Simulating... done!' )	

	def onStep( self ):
		print( "Simulation step..." )

		for c in self._cars:
			affluence_url = "getAffluence/{}".format( self._current_hour_of_day )
			affluence_res = self._fetch_gateway( affluence_url )
			affluence = int( affluence_res[ 'affluence' ] )
			self._log( affluence_res )

			travel_distance_url = "getTravelDistance"
			travel_distance_res = self._fetch_gateway( travel_distance_url )
			travel_distance = float( travel_distance_res[ 'travel_distance' ] )
			self._log( travel_distance_res )

			charging_period_duration_url = "getChargingPeriodDuration"
			charging_period_duration_res = self._fetch_gateway( charging_period_duration_url )
			charging_period_duration = int( charging_period_duration_res[ 'charging_period_duration' ] )
			self._log( charging_period_duration_res )

			charging_period_peak_url = "getChargingPeriodPeak"
			charging_period_peak_res = self._fetch_gateway( charging_period_peak_url )
			charging_period_peak = float( charging_period_peak_res[ 'charging_period_peak' ] )
			self._log( charging_period_peak_res )

			initial_battery_level = 11	
			final_battery_level_url = "getFinalBatteryLevel/{}/{}".format( initial_battery_level, travel_distance )
			final_battery_level_res = self._fetch_gateway( final_battery_level_url )
			final_battery_level = int( final_battery_level_res[ 'final_battery_level' ] )
			self._log( final_battery_level_res )

		self._minutes_simulated = self._minutes_simulated + self._getConfig( 'minutes_per_sim_step' )

		print( 'Simulation step... done!' )
		#TODO

	def _fetch_gateway( self, endpoint ):
		response = requests.get( Simulator.GATEWAY_REQUEST_BASE.format( endpoint ) )
		response_json = response.json( )

		return response_json


