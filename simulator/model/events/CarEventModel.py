from datetime import date, datetime, timedelta
from sqlobject import *

class CarEventModel( SQLObject ):

	_car = ForeignKey( 'CarModel', default = None, dbName = 'car_id' )	
	_start_datetime = DateTimeCol( default = datetime( 1, 1, 1 ), dbName = 'start_datetime' )
	_end_datetime = DateTimeCol( default = datetime( 1, 1, 1 ), dbName = 'end_datetime' )

	def get_car( self ):
		return self._car

	def get_start_datetime( self ):
		return self._start_datetime

	def get_end_datetime( self ):
		return self._end_datetime

	def set_start_datetime( self, start_datetime ):
		self._start_datetime = start_datetime

	def set_end_datetime( self, end_datetime ):
		self._end_datetime = end_datetime
