import time
import threading
import requests
from datetime import date, datetime, timedelta
from .SingletonMetaClass import SingletonMetaClass
from .ConfigurationHelper import ConfigurationHelper
from .Car import Car

class Simulator( metaclass = SingletonMetaClass ):

	GATEWAY_REQUEST_BASE = 'http://cont_energysim_gateway:8000/{}'

	TRAVEL_DURATION = 10 #TODO		

	_main_thread = None	
	_config = { }
	_cars = [ ]

	_current_datetime = None
	_affluence_counts = { }

	def on_init( self ):
		self._current_datetime_lock = threading.Lock( )	
		self._affluence_counts_lock = threading.Lock( )	
		self._fetch_config( )
		self._main_thread = threading.Thread( target = self.run )
		self._main_thread.start( )

	def _fetch_config( self ):
		print( "========== Fetching config..." )
		self._config = ConfigurationHelper.read_config( )
		self.log( self._config )
		print( "========== Fetching config... done!" )

	def log( self, message ):
		is_debug_enabled = self.get_config( 'enable_debug_mode' )
		if is_debug_enabled == True:
			print( message )

	def get_config( self, config_key ):
		return self._config[ config_key ]

	def run( self ):	
		self._initialize_cars( )
		self._initialize_datetime( )
		self._begin_simulation( )

	def _initialize_cars( self ):
		print( '========== Initializing cars...' )
		number_of_cars = self.get_config( 'number_of_cars' )
		for n in range( number_of_cars ):
			self._cars.append( Car( self ) )
		print( '========== Initializing cars... done!' )

	def _initialize_datetime( self ):
		print( '========== Initializing date...' )
		today_date = date.today( )
		today_year = today_date.year
		today_month = today_date.month
		today_day = today_date.day
		self.set_current_datetime( datetime( year = today_year, month = today_month, day = today_day ) )
		print( 'Date initialized as: {}'.format( self._current_datetime ) )
		print( '========== Initializing date... done!' )

	def get_current_datetime( self ):
		with self._current_datetime_lock:
			return self._current_datetime

	def set_current_datetime( self, new_datetime ):
		with self._current_datetime_lock:
			self._current_datetime = new_datetime

	def _begin_simulation( self ):
		print( '========== Simulating...' )
		sim_sampling_rate = self.get_config( 'sim_sampling_rate' )		
		number_of_steps = self.get_config( 'number_of_steps' )
		for n in range( number_of_steps ):
			self.on_step( )
			time.sleep( sim_sampling_rate / 1000 )	
		print( '========== Simulating... done!' )	

	def on_step( self ):
		print( "> Simulation step..." )

		current_datetime = self.get_current_datetime( )

		print( "( ( ( Date: {} ) ) )".format( current_datetime ) )

		current_datetime_str = current_datetime.isoformat( )		

		current_hour_of_day = current_datetime.hour
		affluence_url = "getAffluence/{}".format( current_hour_of_day )
		affluence_res = self.fetch_gateway( affluence_url )
		affluence = int( affluence_res[ 'affluence' ] )
		self._affluence_counts[ current_datetime_str ] = affluence			
		self.log( affluence_res )		

		for c in self._cars:
			travel_distance_url = "getTravelDistance"
			travel_distance_res = self.fetch_gateway( travel_distance_url )
			travel_distance = float( travel_distance_res[ 'travel_distance' ] )
			self.log( travel_distance_res )			

			initial_battery_level = c.get_battery_level( )	
			final_battery_level_url = "getFinalBatteryLevel/{}/{}".format( initial_battery_level, travel_distance )
			final_battery_level_res = self.fetch_gateway( final_battery_level_url )
			final_battery_level = int( final_battery_level_res[ 'final_battery_level' ] )
			self.log( final_battery_level_res )

			travel_start_datetime = current_datetime
			travel_end_datetime = travel_start_datetime + timedelta( minutes = Simulator.TRAVEL_DURATION ) #TODO
			battery_consumption = initial_battery_level - final_battery_level
			c.start_travel( travel_start_datetime, travel_end_datetime, travel_distance, battery_consumption )

			charging_period_duration_url = "getChargingPeriodDuration"
			charging_period_duration_res = self.fetch_gateway( charging_period_duration_url )
			charging_period_duration = int( charging_period_duration_res[ 'charging_period_duration' ] )
			self.log( charging_period_duration_res )

			charging_period_peak_url = "getChargingPeriodPeak"
			charging_period_peak_res = self.fetch_gateway( charging_period_peak_url )
			charging_period_peak = float( charging_period_peak_res[ 'charging_period_peak' ] )
			self.log( charging_period_peak_res )		

			charging_period_start_datetime = current_datetime
			charging_period_end_datetime = charging_period_start_datetime + timedelta( minutes = charging_period_duration )
			c.start_charging_period( charging_period_start_datetime, charging_period_end_datetime,charging_period_peak )								

		minutes_per_sim_step = self.get_config( 'minutes_per_sim_step' )
		self.set_current_datetime( current_datetime + timedelta( minutes = minutes_per_sim_step ) )

		print( '< Simulation step... done!' )

	def fetch_gateway( self, endpoint ):
		response = requests.get( Simulator.GATEWAY_REQUEST_BASE.format( endpoint ) )
		response_json = response.json( )

		return response_json