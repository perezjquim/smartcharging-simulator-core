import json

from config.ConfigurationHelper import *
from .SocketHelper import *		

class Logger( ):

	def __init__( ):
		raise NotSupportedError

	def log( log_str ):
		print( log_str )

	def log_debug( log_str ):
		config_helper = ConfigurationHelper( )
		is_debug_enabled = config_helper.get_config_by_key( 'enable_debug_mode' )
		if is_debug_enabled:
			Logger.log( 'DEBUG: {}'.format( log_str ) )