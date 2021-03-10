import threading
import time
from datetime import date, datetime, timedelta

class CarEvent:

	_car = None
	_start_datetime = None
	_end_datetime = None
	_thread = None

	def __init__( self, car ):
		self._car = car

		self._thread = threading.Thread( target = self.run )
		self._thread.start( )		

	def run( self ):
		raise NotImplementedError		

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

	def destroy( self ):
		self._thread.join( )

	def get_data( self ):
		car = self._car
		car_id = car.get_id( )

		start_datetime_str = ''
		end_datetime_str = ''
		
		if self._start_datetime:
			start_datetime_str = self._start_datetime.isoformat( )

		if self._end_datetime:
			end_datetime_str = self._end_datetime.isoformat( )

		return {
			'car_id' : car_id,
			'start_datetime' : start_datetime_str,
			'end_datetime' : end_datetime_str
		}