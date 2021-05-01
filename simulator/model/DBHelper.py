from sqlobject import *
import os

from base.SingletonMetaClass import SingletonMetaClass

class DBHelper( metaclass = SingletonMetaClass ):

	__PROVIDER = 'sqlite'
	__FILE_PATH = 'db/energysim.db'
	__OPTIONS = '?timeout=15'

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
		from .SimulationModel import SimulationModel
		from .objects.CarModel import CarModel
		from .objects.PlugModel import PlugModel
		from .objects.LogModel import LogModel
		from .events.TravelModel import TravelModel
		from .events.ChargingPeriodModel import ChargingPeriodModel
		from .objects.StatModel import StatModel

		SimulationModel.createTable( ifNotExists = True )
		CarModel.createTable( ifNotExists = True )
		PlugModel.createTable( ifNotExists = True )
		LogModel.createTable( ifNotExists = True )
		TravelModel.createTable( ifNotExists = True )
		ChargingPeriodModel.createTable( ifNotExists = True )
		StatModel.createTable( ifNotExists = True )