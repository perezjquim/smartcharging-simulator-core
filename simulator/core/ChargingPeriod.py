from . import *

class ChargingPeriod:

	_car = None
	_start_datetime = None
	_end_datetime = None
	_peak_value = 0

	def __init__( self, car, start_datetime, end_datetime, peak_value ):
		self._car = car
		self._start_datetime = start_datetime
		self._end_datetime = end_datetime
		self._peak_value = peak_value

	def get_car( self ):
		return self._car

	def get_start_datetime( self ):
		return self._start_datetime

	def get_end_datetime( self ):
		return self._end_datetime

	def get_peak_value( self ):
		return self._peak_value		
