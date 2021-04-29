import threading
from sqlobject import *

from base.SingletonMetaClass import SingletonMetaClass
from config.ConfigurationHelper import ConfigurationHelper
from data.Logger import Logger
from data.DataExporter import DataExporter
from data.SocketHelper import SocketHelper
from base.DebugHelper import DebugHelper
from .Simulation import Simulation

class Simulator( metaclass = SingletonMetaClass ):

	MAIN_LOG_PREFIX = '============================'

	_socket_helper = None
	_data_exporter = None

	_current_simulation = None

	_is_simulation_running = False
	_is_simulation_running_lock = None	

	def on_init( self ):		
		self._socket_helper = SocketHelper( )
		self._socket_helper.on_init( )	

		self._data_exporter = DataExporter( )
		self._data_exporter.on_init( )		

		self._is_simulation_running_lock = threading.Lock( )

		self._socket_helper.attach_on_client_connected( self.on_client_connected )	
		self._socket_helper.attach_on_client_message_received( self.on_client_message_received )		

	def on_start( self ):
		if self.is_simulation_running( ):			
			self.log( 'Simulation cannot be started (it is already running)!' )
		else:
			self.log_main( 'Starting simulation...' )
			self._current_simulation = Simulation( self )
			self._data_exporter.on_init( )		
			self._current_simulation.on_start( )
			self.set_simulation_state( True )	

			self.log_main( 'Starting simulation... done!' )				

	def on_stop( self ):
		if self.is_simulation_running( ):			
			self.log_main( 'Stopping simulation!' )
			self._current_simulation.on_stop( )	
			self.set_simulation_state( False )
		else:
			self.log( 'Simulation cannot be stopped (it is not running)!' )		

	def on_client_connected( self, client ):		
		self._send_sim_state_to_clients( client )
		self.send_sim_data_to_clients( client )		

	def _send_sim_state_to_clients( self, client = None ):
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

	def send_sim_data_to_clients( self, client=None ):
		self.log_debug( '////// SENDING SIM DATA... //////' )

		current_simulation = self._current_simulation

		if current_simulation:

			current_simulation.lock_current_datetime( )

			simulation_data = self._data_exporter.prepare_simulation_data( self )

			self._socket_helper.send_message_to_clients( 'data', simulation_data, client )		

			current_simulation.unlock_current_datetime( )

		self.log_debug( '////// SENDING SIM DATA... done! //////' )			

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