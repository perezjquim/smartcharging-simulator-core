import json
import threading

from base.SingletonMetaClass import *

class ConfigurationHelper( metaclass = SingletonMetaClass ):

	CONFIG_FILE_NAME = 'simulator/config.json'	

	_lock = None
	_config = None

	def __init__( self ):
		self._lock = threading.Lock( )

	def get_config( self ):
		self._lock.acquire( )

		if not self._config:
			self._read_config( )		

		config = self._config

		self._lock.release( )

		return config

	def set_config( self, new_config ):
		self._lock.acquire( )		

		self._config = new_config

		self._lock.release( )

	def get_config_by_key( self, config_key ):
		self._lock.acquire( )

		if not self._config:
			self._read_config( )

		config_value = self._config[ config_key ]

		self._lock.release( )

		return config_value

	def set_config_by_key( self, config_key, config_value ):
		self._lock.acquire( )

		if not self._config:
			self._read_config( )

		self._config[ config_key ] = config_value

		self._lock.release( )	

	def _read_config( self ):
		with open( ConfigurationHelper.CONFIG_FILE_NAME ) as file:
	    		self._config = json.load( file )