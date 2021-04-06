from peewee import *

from base.ImportHelper import ImportHelper

SingletonMetaClass = ImportHelper.import_class( 'base.SingletonMetaClass' )
Car = ImportHelper.import_class( 'core.Car' )
Plug = ImportHelper.import_class( 'core.Plug' )
ChargingPeriod = ImportHelper.import_class( 'core.events.ChargingPeriod' )
Travel = ImportHelper.import_class( 'core.events.Travel' )

class DBHelper( metaclass = SingletonMetaClass ):

	__FILE_PATH = 'db/energysim.db'
	__PRAGMAS = { 'journal_mode' : 'wal' }

	_db = None

	def __init__( self ):
		self._db = sqliteDatabase( DBHelper.__FILE_PATH, pragmas = DBHelper.__PRAGMAS )
		self._prepare( )

	def _prepare( self ):
		self._db.create_tables( [ Car, Plug, ChargingPeriod, Travel ] )

	def get_db( self ):
		return self._db