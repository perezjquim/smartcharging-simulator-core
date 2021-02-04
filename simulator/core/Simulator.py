from . import *
from data import *
import time
import importlib
import threading
import requests
from datetime import date, datetime, timedelta

class Simulator:

	GATEWAY_REQUEST_BASE = 'http://cont_energysim_gateway:8000/{}'

	_run_thread = None	
	_config = [ ]
	_cars = [ ]
	_current_datetime = None

	def __init__( self ):
		pass
		#TODO	

	def onInit( self ):
		self._fetch_config( )
		self._run_thread = threading.Thread( target = self.run )
		self._run_thread.start( )

	def _fetch_config( self ):
		print( "========== Fetching config..." )
		self._config = ConfigurationHelper.read_config( )
		self._log( self._config )
		print( "========== Fetching config... done!" )

	def _log( self, message ):
		is_debug_enabled = self._getConfig( 'enable_debug_mode' )
		if is_debug_enabled == True:
			print( message )

	def _getConfig( self, config_key ):
		return self._config[ config_key ]

	def run( self ):	
		self._initialize_cars( )
		self._initialize_date( )
		self._begin_simulation( )

	def _initialize_cars( self ):
		print( '========== Initializing cars...' )
		number_of_cars = self._getConfig( 'number_of_cars' )
		for n in range( number_of_cars ):
			self._cars.append( Car( ) )
		print( '========== Initializing cars... done!' )

	def _initialize_date( self ):
		print( '========== Initializing date...' )
		today_date = date.today( )
		today_year = today_date.year
		today_month = today_date.month
		today_day = today_date.day
		self._current_datetime = datetime( year = today_year, month = today_month, day = today_day )
		print( 'Date initialized as: {}'.format( self._current_datetime ) )
		print( '========== Initializing date... done!' )

	def _begin_simulation( self ):
		print( '========== Simulating...' )
		sim_sampling_rate = self._getConfig( 'sim_sampling_rate' )		
		number_of_steps = self._getConfig( 'number_of_steps' )
		for n in range( number_of_steps ):
			self.on_step( )
			time.sleep( sim_sampling_rate / 1000 )	
		print( '========== Simulating... done!' )	

	def on_step( self ):
		print( "> Simulation step..." )

		print( "( ( ( Date: {} ) ) )".format( self._current_datetime ) )

		current_hour_of_day = self._current_datetime.hour
		affluence_url = "getAffluence/{}".format( current_hour_of_day )
		affluence_res = self._fetch_gateway( affluence_url )
		affluence = int( affluence_res[ 'affluence' ] )
		self._log( affluence_res )		

		for c in self._cars:
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

		minutes_per_sim_step = self._getConfig( 'minutes_per_sim_step' )
		self._current_datetime += timedelta( minutes = minutes_per_sim_step )

		print( '< Simulation step... done!' )

	def _fetch_gateway( self, endpoint ):
		response = requests.get( Simulator.GATEWAY_REQUEST_BASE.format( endpoint ) )
		response_json = response.json( )

		return response_json