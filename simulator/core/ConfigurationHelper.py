import json
from .SingletonMetaClass import SingletonMetaClass

CONFIG_FILE_NAME = 'simulator/config.json'

class ConfigurationHelper( metaclass = SingletonMetaClass ):

	def read_config( ):
		print( "Reading config..." );

		with open( CONFIG_FILE_NAME ) as file:
	    		config = json.load( file )

	    		print( "Reading config... done!" )
	    		return config