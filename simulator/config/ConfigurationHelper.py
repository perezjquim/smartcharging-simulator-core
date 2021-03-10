import json
from base.SingletonMetaClass import SingletonMetaClass

class ConfigurationHelper( metaclass = SingletonMetaClass ):

	CONFIG_FILE_NAME = 'simulator/config.json'	

	def read_config( ):
		with open( ConfigurationHelper.CONFIG_FILE_NAME ) as file:
	    		config = json.load( file )
	    		return config