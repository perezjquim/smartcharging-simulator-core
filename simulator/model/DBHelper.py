from pony.orm import *

from base.SingletonMetaClass import SingletonMetaClass

class DBHelper( metaclass = SingletonMetaClass ):

	__PROVIDER = 'sqlite'
	__FILE_PATH = '../../db/energysim.sqlite'

	_db = None

	def __init__( self ):
		self._db = Database( provider = DBHelper.__PROVIDER, filename = DBHelper.__FILE_PATH, create_db = True )	

	def on_init( self ):
		self._prepare( )

	def _prepare( self ):			
		from core.Car import Car
		from core.Plug import Plug
		from core.events.Travel import Travel
		from core.events.ChargingPeriod import ChargingPeriod

		self._db.generate_mapping( create_tables = True )

	def get_entity_class( self ):		
		entity = self._db.Entity
		return entity