from sqlobject import *
import os

from base.SingletonMetaClass import SingletonMetaClass

class DBHelper( metaclass = SingletonMetaClass ):

	__PROVIDER = 'sqlite'
	__FILE_PATH = 'db/energysim.db'
	__OPTIONS = '?timeout=15'

	_db = None

	def __init__( self ):
		db_filename = os.path.abspath( DBHelper.__FILE_PATH )	
		connection_string = '{}:{}{}'.format( DBHelper.__PROVIDER, db_filename, DBHelper.__OPTIONS )
		connection = connectionForURI( connection_string )
		self._prepare( connection )
		sqlhub.processConnection = connection

	def on_init( self ):
		self._prepare_tables( )

	def _prepare( self, connection ):
		connection.queryAll( 'pragma journal_mode = wal;' )
		connection.queryAll( 'pragma synchronous = normal;' )
		connection.queryAll( 'pragma temp_store = memory;' )

	def _prepare_tables( self ):			
		from core.Car import Car
		from core.Plug import Plug
		from core.events.Travel import Travel
		from core.events.ChargingPeriod import ChargingPeriod

		Car.createTable( ifNotExists = True )
		Plug.createTable( ifNotExists = True )
		Travel.createTable( ifNotExists = True )
		ChargingPeriod.createTable( ifNotExists = True )