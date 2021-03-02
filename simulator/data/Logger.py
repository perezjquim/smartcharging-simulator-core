import json
from core.SingletonMetaClass import SingletonMetaClass
from core.ConfigurationHelper import ConfigurationHelper
from .SocketHelper import SocketHelper

class Logger( metaclass = SingletonMetaClass ):

	def log( log_str ):
		socket_helper = SocketHelper( )
		socket_helper.send_message_to_clients( 'log', log_str )
		print( log_str )

	def log_debug( log_str ):
		config = ConfigurationHelper.read_config( )
		is_debug_enabled = config[ 'enable_debug_mode' ]
		if is_debug_enabled:
			Logger.log( 'DEBUG: {}'.format( log_str ) )