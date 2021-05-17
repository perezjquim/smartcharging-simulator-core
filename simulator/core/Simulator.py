import threading

from base.SingletonMetaClass import *
from config.ConfigurationHelper import *
from data.Logger import *
from data.SocketHelper import *
from base.DebugHelper import *
from .Simulation import *
from model.DBHelper import *

class Simulator( metaclass = SingletonMetaClass ):

	MAIN_LOG_PREFIX = '============================'

	_socket_helper = None

	_current_simulation = None

	def on_init( self ):		
		self._socket_helper = SocketHelper( )
		self._socket_helper.on_init( )	
		self._socket_helper.attach_on_client_connected( self.on_client_connected )	
		self._socket_helper.attach_on_client_message_received( self.on_client_message_received )

		self._current_simulation = None
		
	def on_start( self ):
		current_simulation = self._current_simulation

		if current_simulation and current_simulation.is_simulation_running( ):			
			self.log( 'Simulation cannot be started (it is already running)!' )
		else:			
			self.log_main( 'Starting simulation...' )

			self._current_simulation = None
			self._current_simulation = Simulation( self )			
			self._current_simulation.on_start( )

			self.send_sim_list_to_clients( )

			self.log_main( 'Starting simulation... done!' )

	def on_stop( self ):
		current_simulation = self._current_simulation

		if current_simulation and current_simulation.is_simulation_running( ):
			self.log_main( 'Stopping simulation...' )

			current_simulation.on_stop( )	

			self.log_main( 'Stopping simulation... done!' )				

		else:
			self.log( 'Simulation cannot be stopped (it is not running)!' )		

	def get_current_simulation( self ):
		return self._current_simulation

	def on_client_connected( self, client ):		
		self.send_sim_state_to_clients( client )
		self.send_sim_list_to_clients( client )		
		self.send_sim_data_to_clients( client )		

	def send_sim_state_to_clients( self, client = None ):
		self.log_debug( '////// SENDING SIM STATE... //////' )

		current_simulation = self._current_simulation

		is_sim_running = False
		
		if current_simulation:
			is_sim_running = current_simulation.is_simulation_running( )
		
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

				current_simulation = self._current_simulation

				if current_simulation:					
					plug_id = command_args[ 'plug_id' ]
					plug_new_status = command_args[ 'plug_new_status' ]
					current_simulation.set_charging_plug_status( plug_id, plug_new_status )

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

	def send_sim_list_to_clients( self, client = None ):
		self.log_debug( '////// SENDING SIM LIST... //////' )		

		sim_list = Simulation.get_sim_list( self._current_simulation )
		self._socket_helper.send_message_to_clients( 'sim_list', sim_list, client )		

		self.log_debug( '////// SENDING SIM LIST... done! //////' )					

	def send_sim_data_to_clients( self, client=None ):
		self.log_debug( '////// SENDING SIM DATA... //////' )

		current_simulation = self._current_simulation

		if current_simulation:

			current_simulation.lock_current_datetime( )

			simulation_data = current_simulation.get_simulation_data( )

			self._socket_helper.send_message_to_clients( 'data', simulation_data, client )		

			current_simulation.unlock_current_datetime( )

		self.log_debug( '////// SENDING SIM DATA... done! //////' )			

	def export_data( self ):
		db_helper = DBHelper( )
		exported_data = db_helper.export_data( )
		return exported_data