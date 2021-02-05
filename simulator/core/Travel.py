from . import *

class Travel:

	_car = None
	_start_datetime = None
	_end_datetime = None
	_distance = 0
	_battery_consumption = 0	

	def __init__( self, car, start_datetime, end_datetime, distance, battery_consumption ):
		self._car = car
		self._start_datetime = start_datetime
		self._end_datetime = end_datetime
		self._distance = distance
		self._battery_consumption = battery_consumption		

	def get_car( self ):
		return self._car

	def get_start_datetime( self ):
		return self._start_datetime

	def get_end_datetime( self ):
		return self._end_datetime

	def get_distance( self ):
		return self._distance

	def get_battery_consumption( self ):
		return self._battery_consumption		