from peewee import *

from base.SingletonMetaClass import SingletonMetaClass

class DBHelper( metaclass = SingletonMetaClass ):

	__FILE_PATH = 'db/energysim.db'
	__PRAGMAS = { 'journal_mode' : 'wal' }

	_db = None

	def __init__( self ):
		self._db = SqliteDatabase( DBHelper.__FILE_PATH, pragmas = DBHelper.__PRAGMAS )

	def on_init( self ):
		self._prepare( )

	def _prepare( self ):
		from core.Car import Car
		from core.Plug import Plug
		from core.events.ChargingPeriod import ChargingPeriod
		from core.events.Travel import Travel

		models = [ Car, Plug, ChargingPeriod, Travel ] 

		for m in models:
			m._meta.set_database( self._db )

		self._db.create_tables( models )