import time
import threading
import requests
from datetime import date, datetime, timedelta
from .SingletonMetaClass import SingletonMetaClass
from .ConfigurationHelper import ConfigurationHelper
from .Car import Car

class Simulator( metaclass = SingletonMetaClass ):

	GATEWAY_REQUEST_BASE = 'http://cont_energysim_gateway:8000/{}'

	_main_thread = None	
	_config = { }
	_cars = [ ]

	_current_step = 1
	_current_datetime = None
	_affluence_counts = { }

	_current_step_lock = None
	_current_datetime_lock = None
	_affluence_counts_lock	 = None

	def on_init( self ):
		self._current_step_lock = threading.Lock( )
		self._current_datetime_lock = threading.Lock( )	
		self._affluence_counts_lock = threading.Lock( )	
		self._fetch_config( )
		self._initialize_cars( )
		self._initialize_datetime( )	
		self._current_step = 1	
		self._main_thread = threading.Thread( target = self.run )
		self._main_thread.start( )

	def _fetch_config( self ):
		self.log( "========== Fetching config..." )
		self._config = ConfigurationHelper.read_config( )
		self.log_debug( self._config )
		self.log( "========== Fetching config... done!" )

	def log( self, message ):
		print( message )

	def log_debug( self, message ):
		is_debug_enabled = self.get_config( 'enable_debug_mode' )
		if is_debug_enabled:
			self.log( 'DEBUG: {}'.format( message ) )

	def get_config( self, config_key ):
		return self._config[ config_key ]

	def run( self ):	
		self._begin_simulation( )

	def _initialize_cars( self ):
		self.log( '========== Initializing cars...' )

		number_of_cars = self.get_config( 'number_of_cars' )
		for n in range( number_of_cars ):
			self._cars.append( Car( self ) )

		self.log( '========== Initializing cars... done!' )

	def _initialize_datetime( self ):
		self.log( '========== Initializing date...' )

		today_date = date.today( )
		today_year = today_date.year
		today_month = today_date.month
		today_day = today_date.day

		self.set_current_datetime( datetime( year = today_year, month = today_month, day = today_day ) )
		self.log( 'Date initialized as: {}'.format( self._current_datetime ) )

		self.log( '========== Initializing date... done!' )

	def get_current_datetime( self ):
		with self._current_datetime_lock:
			return self._current_datetime

	def set_current_datetime( self, new_datetime ):
		with self._current_datetime_lock:
			self._current_datetime = new_datetime

	def increment_current_datetime( self, minutes ):
		with self._current_datetime_lock:
			self._current_datetime += timedelta( minutes = minutes )

	def _begin_simulation( self ):
		self.log( '========== Simulating...' )

		sim_sampling_rate = self.get_config( 'sim_sampling_rate' )		

		number_of_steps = self.get_config( 'number_of_steps' )
		while True:
			cars_in_travel = [ c for c in self._cars if c.is_traveling( ) ]
			cars_in_charging = [ c for c in self._cars if c.is_charging( ) ]

			current_step = self.get_current_step( )
			is_simulation_running = ( current_step <= number_of_steps or len( cars_in_travel ) > 0 or len( cars_in_charging ) > 0 )
			
			if is_simulation_running:			
				self.on_step( )
				time.sleep( sim_sampling_rate / 1000 )
			else:
				break

		self.log( '========== Simulating... done!' )	

	def can_simulate_new_actions( self ):
		with self._current_step_lock:
			number_of_steps = self.get_config( 'number_of_steps' )
			can_simulate_new_actions = ( self._current_step <= number_of_steps )
			return can_simulate_new_actions

	def get_current_step( self ):
		with self._current_step_lock:
			return self._current_step

	def increment_step( self ):
		with self._current_step_lock:
			self._current_step += 1

	def on_step( self ):
		self.log( "> Simulation step..." )

		current_datetime = self.get_current_datetime( )
		
		self.log( "( ( ( Step started at: {} ) ) )".format( current_datetime ) )

		if self.can_simulate_new_actions( ):

			current_datetime_str = current_datetime.strftime( '%Y%m%d%H' )

			if current_datetime_str in self._affluence_counts:
				pass
			else:
				current_hour_of_day = current_datetime.hour
				affluence_url = "getAffluence/{}".format( current_hour_of_day )
				affluence_res = self.fetch_gateway( affluence_url )
				affluence = int( affluence_res[ 'affluence' ] )
				self._affluence_counts[ current_datetime_str ] = affluence			
				self.log_debug( affluence_res )

			if self._affluence_counts[ current_datetime_str ] > 0:		

				for c in self._cars:
					c.lock( )

					car_can_travel = ( not c.is_traveling( ) and not c.is_charging( ) )
					if car_can_travel:
						c.start_new_travel( )	

					c.unlock( )

		else:
			self.log( '-- Simulation period ended: this step is only used to resume travels and/or charging periods! --' )

		minutes_per_sim_step = self.get_config( 'minutes_per_sim_step' )
		self.increment_current_datetime( minutes_per_sim_step )
		self.increment_step( )

		current_datetime = self.get_current_datetime( )
		self.log( "( ( ( Step ended at: {} ) ) )".format( current_datetime ) )		

		self.log( '< Simulation step... done!' )

	def fetch_gateway( self, endpoint ):
		response = requests.get( Simulator.GATEWAY_REQUEST_BASE.format( endpoint ) )
		response_json = response.json( )

		return response_json

