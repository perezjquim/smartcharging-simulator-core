from . import *

class Car:

	_isTraveling: False
	_isCharging: False
	_travels: [ ]

	def __init__( self ):
		self._batteryLevel = 10
		#TODO

	def get_battery_level( self ):
		return self._batteryLevel

	def set_battery_level( self, batteryLevel ):
		self._batteryLevel = batteryLevel

	def start_travel( self, distance, start_datetime, end_datetime ):
		new_travel = Travel( self, distance, start_datetime, end_datetime )
		self._travels.push( new_travel )