from . import *
import json

CONFIG_FILE_NAME = 'config.json'

class ConfigurationHelper:

	def readConfig( ):
		print( "Reading config..." );

		with open( CONFIG_FILE_NAME ) as file:
	    		config = json.load( file )

	    		print( "Reading config... done!" )
	    		return config