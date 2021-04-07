import json

from base.ImportHelper import ImportHelper

"""
SingletonMetaClass = ImportHelper.import_class( 'base.SingletonMetaClass' )
ConfigurationHelper = ImportHelper.import_class( 'config.ConfigurationHelper' )
SocketHelper = ImportHelper.import_class( 'data.SocketHelper' )
"""

class Logger( ):

	def __init__( ):
		raise NotSupportedError

	def log( log_str ):
		socket_helper = SocketHelper( )
		socket_helper.send_message_to_clients( 'log', log_str )
		print( log_str )

	def log_debug( log_str ):
		config_helper = ConfigurationHelper( )
		is_debug_enabled = config_helper.get_config_by_key( 'enable_debug_mode' )
		if is_debug_enabled:
			Logger.log( 'DEBUG: {}'.format( log_str ) )