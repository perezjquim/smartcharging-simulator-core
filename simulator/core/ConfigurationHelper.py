import json
from .SingletonMetaClass import SingletonMetaClass

class ConfigurationHelper( metaclass = SingletonMetaClass ):

	CONFIG_FILE_NAME = 'simulator/config.json'	

	def read_config( ):
		print( "Reading config..." );

		with open( ConfigurationHelper.CONFIG_FILE_NAME ) as file:
	    		config = json.load( file )

	    		print( "Reading config... done!" )
	    		return config