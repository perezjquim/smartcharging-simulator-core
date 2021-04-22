from sqlobject import *
import os

from base.SingletonMetaClass import SingletonMetaClass

class DBHelper( metaclass = SingletonMetaClass ):

	__PROVIDER = 'sqlite'
	__FILE_PATH = 'db/energysim.db'
	__OPTIONS = '?debug=1&debugOutput=1&cache=0'

	_db = None

	def __init__( self ):
		db_filename = os.path.abspath( DBHelper.__FILE_PATH )	
		connection_string = '{}:{}{}'.format( DBHelper.__PROVIDER, db_filename, DBHelper.__OPTIONS )
		print( connection_string )
		connection = connectionForURI( connection_string )	
		sqlhub.processConnection = connection

	def on_init( self ):
		self._prepare( )

	def _prepare( self ):			
		from core.Car import Car
		from core.Plug import Plug
		from core.events.Travel import Travel
		from core.events.ChargingPeriod import ChargingPeriod

		Car.createTable( ifNotExists = True )
		Plug.createTable( ifNotExists = True )
		Travel.createTable( ifNotExists = True )
		ChargingPeriod.createTable( ifNotExists = True )

	def get_entity_class( self ):		
		return SQLObject