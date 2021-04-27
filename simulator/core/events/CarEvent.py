import threading
import time
from datetime import date, datetime, timedelta
from sqlobject import *

from core.Car import Car

class CarEvent( SQLObject ):

	_car = ForeignKey( 'Car', default = None, dbName = 'car_id' )	
	_start_datetime = DateTimeCol( default = datetime( 1, 1, 1 ), dbName = 'start_datetime' )
	_end_datetime = DateTimeCol( default = datetime( 1, 1, 1 ), dbName = 'end_datetime' )
	_thread = None

	def start( self ):
		self._thread = threading.Thread( target = self.run )
		self._thread.start( )	

	def run( self ):
		raise NotImplementedError		

	def get_car( self ):
		return self._car

	def set_car( self, car ):
		self._car = car

	def get_start_datetime( self ):
		return self._start_datetime

	def get_end_datetime( self ):
		return self._end_datetime

	def set_start_datetime( self, start_datetime ):
		self._start_datetime = start_datetime

	def set_end_datetime( self, end_datetime ):
		self._end_datetime = end_datetime

	def destroy( self ):
		if self._thread:
			self._thread.join( )

	def get_data( self ):
		car = self.get_car( )
		car_id = car.get_id( )

		start_datetime_str = ''
		end_datetime_str = ''
		
		if self._start_datetime:
			start_datetime_str = self._start_datetime.isoformat( )

		if self._thread and not self._thread.is_alive( ):			
			if self._end_datetime:
				end_datetime_str = self._end_datetime.isoformat( )

		return {
			'id' : self.id,
			'car_id' : car_id,
			'start_datetime' : start_datetime_str,
			'end_datetime' : end_datetime_str
		}
