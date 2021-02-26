import json
from .SingletonMetaClass import SingletonMetaClass
from .ConfigurationHelper import ConfigurationHelper
from data.SocketHelper import SocketHelper

class Logger( metaclass = SingletonMetaClass ):

	def log( message ):
		socket_helper = SocketHelper( )
		socket_helper.send_message_to_clients( message )
		print( message )

	def log_debug( message ):
		config = ConfigurationHelper.read_config( )
		is_debug_enabled = config[ 'enable_debug_mode' ]
		if is_debug_enabled:
			self.log( 'DEBUG: {}'.format( message ) )