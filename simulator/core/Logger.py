import json
from .SingletonMetaClass import SingletonMetaClass
from .ConfigurationHelper import ConfigurationHelper
from .SingletonMetaClass import SingletonMetaClass

class Logger( metaclass = SingletonMetaClass ):

	def log( message ):
		print( message )

	def log_debug( message ):
		config = ConfigurationHelper.read_config( )
		is_debug_enabled = config[ 'enable_debug_mode' ]
		if is_debug_enabled:
			self.log( 'DEBUG: {}'.format( message ) )