import time
import threading
import requests
from datetime import date, datetime, timedelta
from sqlobject import *

from base.SingletonMetaClass import SingletonMetaClass
from config.ConfigurationHelper import ConfigurationHelper
from data.Logger import Logger
from data.DataExporter import DataExporter
from data.SocketHelper import SocketHelper
from base.DebugHelper import DebugHelper
from .Car import Car
from .Plug import Plug
from .events.Travel import Travel
from .events.ChargingPeriod import ChargingPeriod

class Simulator( metaclass = SingletonMetaClass ):

	MAIN_LOG_PREFIX = '============================'

	__counter = 0
	_current_simulation_id = 0

	_socket_helper = None
	_data_exporter = None

	_main_thread = None	
	_cars = [ ]

	_affluence_counts = { }

	_current_step = 1
	_current_step_lock = None

	_current_datetime = None	
	_current_datetime_lock = None

	_charging_plugs = [ ]

	_is_simulation_running = False
	_is_simulation_running_lock = None	

	def on_init( self ):		
		self._socket_helper = SocketHelper( )
		self._socket_helper.on_init( )	

		self._data_exporter = DataExporter( )
		self._data_exporter.on_init( )		

		self._current_step_lock = threading.Lock( )
		self._current_datetime_lock = threading.Lock( )
		self._is_simulation_running_lock = threading.Lock( )

		self._socket_helper.attach_on_client_connected( self.on_client_connected )	
		self._socket_helper.attach_on_client_message_received( self.on_client_message_received )		

	def on_start( self ):
		if self.is_simulation_running( ):			
			self.log( 'Simulation cannot be started (it is already running)!' )
		else:
			self.log_main( 'Starting simulation...' )
			Simulator.__counter += 1
			self._current_simulation_id = Simulator.__counter
			self._data_exporter.on_init( )
			self._initialize_cars( )
			self._initialize_plugs( )
			self._initialize_datetime( )	
			self._current_step = 1			
			self.set_simulation_state( True )	
			self._main_thread = threading.Thread( target = self.run )						
			self._main_thread.start( )
			self.log_main( 'Starting simulation... done!' )				

	def on_stop( self ):
		if self.is_simulation_running( ):			
			self.log_main( 'Stopping simulation!' )
			self._end_simulation( True )		
		else:
			self.log( 'Simulation cannot be stopped (it is not running)!' )		

	def _end_simulation( self, wait_for_main_thread ):
		self.set_simulation_state( False )

		for c in self._cars:
			c.destroy( )	

		if wait_for_main_thread:					
			self._main_thread.join( )

		self._send_sim_data_to_clients( )

	def on_client_connected( self, client ):		
		self._send_sim_state_to_clients( client )
		self._send_sim_data_to_clients( client )		

	def _send_sim_state_to_clients( self, client=None ):
		self.log_debug( '////// SENDING SIM STATE... //////' )

		is_sim_running = self.is_simulation_running( )
		config = self.get_config( )
		message = { 'is_sim_running' : is_sim_running, 'config' : config }
		self._socket_helper.send_message_to_clients( 'state', message )

		self.log_debug( '////// SENDING SIM STATE... done! //////' )		

	def on_client_message_received( self, message ):	
		self.log_debug( "$$$ MESSAGE RECEIVED: {} $$$".format( message ) )

		message_type = message[ 'message_type' ]
		message_value = message[ 'message_value' ]

		if message_type == 'command':

			command_name = message_value[ 'command_name' ]
			command_args = message_value[ 'command_args' ]

			if command_name == 'START-SIMULATION':

				self.on_start( )

			elif command_name == 'STOP-SIMULATION':

				self.on_stop( )

			elif command_name == 'SET-PLUG-STATUS':

				plug_id = command_args[ 'plug_id' ]
				plug_new_status = command_args[ 'plug_new_status' ]
				self.set_charging_plug_status( plug_id, plug_new_status )

			elif command_name == 'SET-CONFIG':

				new_config = command_args[ 'new_config' ]
				self.set_config( new_config )				

			elif command_name == 'SET-CONFIG-BY-KEY':

				config_key = command_args[ 'config_key' ]
				config_new_value = command_args[ 'config_value' ]
				self.set_config_by_key( config_key, config_new_value )

			else:

				self.log( 'Unknown command received - {}'.format( message_value ) )

	def log( self, message ):
		Logger.log( message )

	def log_main( self, message ):
		self.log( '{} {}'.format( Simulator.MAIN_LOG_PREFIX, message ) ) 

	def log_debug( self, message ):
		Logger.log_debug( message )

	def get_config( self ):
		config_helper = ConfigurationHelper( )
		config = config_helper.get_config( )
		return config

	def set_config( self, new_config ):
		config_helper = ConfigurationHelper( )
		config_helper.set_config( new_config )

	def get_config_by_key( self, config_key ):
		config_helper = ConfigurationHelper( )
		config_value = config_helper.get_config_by_key( config_key )
		return config_value

	def set_config_by_key( self, config_key, config_value ):
		config_helper = ConfigurationHelper( )
		config_helper.set_config_by_key( config_key, config_value )

	def get_cars( self ):
		return self._cars

	def get_charging_plugs( self ):
		return self._charging_plugs

	def set_charging_plug_status( self, plug_id, plug_new_status ):
		plug = list( filter( lambda p : p.get_id( ) == plug_id, self._charging_plugs ) )
		plug = plug[ 0 ]
		plug.lock( )
		plug.set_status( plug_new_status )
		plug.unlock( )

	def _initialize_cars( self ):
		self.log( 'Initializing cars...' )

		self._cars = [ ]
		number_of_cars = self.get_config_by_key( 'number_of_cars' )
		for n in range( number_of_cars ):
			self._cars.append( Car( self ) )

		self.log( 'Initializing cars... done!' )

	def _initialize_datetime( self ):
		self.log( 'Initializing date...' )

		today_date = date.today( )
		today_year = today_date.year
		today_month = today_date.month
		today_day = today_date.day

		self.set_current_datetime( datetime( year = today_year, month = today_month, day = today_day ) )
		self.log( 'Date initialized as: {}'.format( self._current_datetime ) )

		self.log( 'Initializing date... done!' )

	def _initialize_plugs( self ):
		self.log( 'Initializing plugs...' )

		self._charging_plugs = [ ]
		number_of_charging_plugs = self.get_config_by_key( 'number_of_charging_plugs' )
		for n in range( number_of_charging_plugs ):
			self._charging_plugs.append( Plug( self ) )

		self.log( 'Initializing plugs... done!' )				

	def lock_current_datetime( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'LOCKING DATETIME... (by {})'.format( caller ) )
		self._current_datetime_lock.acquire( )

	def unlock_current_datetime( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'UNLOCKING DATETIME... (by {})'.format( caller ) )
		self._current_datetime_lock.release( )

	def lock_current_step( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'LOCKING STEP... (by {})'.format( caller ) )
		self._current_step_lock.acquire( )

	def unlock_current_step( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'UNLOCKING STEP... (by {})'.format( caller ) )
		self._current_step_lock.release( )		

	def get_current_datetime( self ):
		return self._current_datetime

	def set_current_datetime( self, new_datetime ):
		self._current_datetime = new_datetime

	def run( self ):
		self.log_main( 'Simulating...' )		

		sim_sampling_rate = self.get_config_by_key( 'sim_sampling_rate' )		
		number_of_steps = self.get_config_by_key( 'number_of_steps' )

		while self.is_simulation_running( ):

			number_of_busy_cars = 0
			total_plug_consumption = 0

			for c in self._cars:
				c.lock( )

				if c.is_busy( ):
					number_of_busy_cars += 1

				car_plug = c.get_plug( )
				if car_plug:
					plug_energy_consumption = car_plug.get_energy_consumption( )
					total_plug_consumption += plug_energy_consumption

				c.unlock( )		

			self.log( '### TOTAL PLUG CONSUMPTION: {} KW ###'.format( total_plug_consumption ) )

			should_simulate_next_step = ( self.can_simulate_new_actions( ) or number_of_busy_cars > 0 )

			if should_simulate_next_step:	

				self.log( "> Simulation step..." )		

				self.lock_current_datetime( )

				current_datetime = self.get_current_datetime( )
				current_step = self.get_current_step( )				
				if current_step > 1:
					
					minutes_per_sim_step = self.get_config_by_key( 'minutes_per_sim_step' )
					current_datetime += timedelta( minutes = minutes_per_sim_step )
					self.set_current_datetime( current_datetime )	

				self.unlock_current_datetime( )
				
				self.log( "( ( ( Step #{} - at: {} ) ) )".format( current_step, current_datetime ) )						

				self.on_step( current_datetime )

				self.lock_current_step( )
				
				current_step += 1
				self.set_current_step( current_step )			

				self.unlock_current_step( )

				self.log( '< Simulation step... done!' )							

			else:

				self._end_simulation( False )		

			self._send_sim_data_to_clients( )

			time.sleep( sim_sampling_rate / 1000 )	
							
		self.log_main( 'Simulating... done!' )	

	def _send_sim_data_to_clients( self, client=None ):
		self.log_debug( '////// SENDING SIM DATA... //////' )

		self.lock_current_datetime( )

		simulation_data = self._data_exporter.prepare_simulation_data( self )

		self._socket_helper.send_message_to_clients( 'data', simulation_data, client )		

		self.unlock_current_datetime( )

		self.log_debug( '////// SENDING SIM DATA... done! //////' )			

	def can_simulate_new_actions( self ):
		number_of_steps = self.get_config_by_key( 'number_of_steps' )
		can_simulate_new_actions = self.is_simulation_running( ) and ( self._current_step <= number_of_steps )
		return can_simulate_new_actions

	def lock_simulation( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'LOCKING SIMULATION... (by {})'.format( caller ) )
		self._is_simulation_running_lock.acquire( )		

	def unlock_simulation( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'UNLOCKING SIMULATION... (by {})'.format( caller ) )
		self._is_simulation_running_lock.release( )			

	def is_simulation_running( self ):
		self.lock_simulation( )
		is_simulation_running = self._is_simulation_running
		self.unlock_simulation( )
		return is_simulation_running

	def set_simulation_state( self, new_value ):
		self.lock_simulation( )
		self._is_simulation_running = new_value
		self.unlock_simulation( )
		self._send_sim_state_to_clients( )		

	def get_current_step( self ):
		return self._current_step

	def set_current_step( self, new_step ):
		self._current_step = new_step

	def on_step( self, current_datetime ):

		if self.can_simulate_new_actions( ):

			current_datetime_str = current_datetime.strftime( '%Y%m%d%H' )

			if current_datetime_str in self._affluence_counts:

				pass
			
			else:

				current_hour_of_day = current_datetime.hour
				affluence_url = "travel/affluence/{}".format( current_hour_of_day )
				affluence_res = self.fetch_gateway( affluence_url )
				affluence = int( affluence_res[ 'affluence' ] )
				self._affluence_counts[ current_datetime_str ] = affluence			

			if self._affluence_counts[ current_datetime_str ] > 0:		

				for c in self._cars:

					c.lock( )

					car_can_travel = ( self.is_simulation_running( ) and not c.is_busy( ) )		
					if car_can_travel:
						c.start_travel( )	
						self._affluence_counts[ current_datetime_str ] -= 1	

					c.unlock( )

					if self._affluence_counts[ current_datetime_str ] < 1:						
						break					

		else:
			
			self.log( '-- Simulation period ended: this step is only used to resume travels and/or charging periods! --' )

	def fetch_gateway( self, endpoint ):
		base_url = self.get_config_by_key( 'gateway_request_base_url' )
		url = base_url.format( endpoint )
		response = requests.get( url )
		response_json = response.json( )
		self.log_debug( '\\\\\\ GATEWAY \\\\\\ URL: {}'.format( url )	 )
		self.log_debug( '\\\\\\ GATEWAY \\\\\\ RESPONSE: {}'.format( response_json ) )

		return response_json