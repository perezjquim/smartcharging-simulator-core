from . import *

class Car:

	DEFAULT_BATTERY_LEVEL = 10

	_is_traveling = False
	_is_charging = False
	_travels = [ ]
	_charging_periods = [ ]

	def __init__( self ):
		self._batteryLevel = Car.DEFAULT_BATTERY_LEVEL
		self._is_traveling = False
		self._is_charging = False
		self._travels = [ ]

	def get_battery_level( self ):
		return self._batteryLevel

	def set_battery_level( self, batteryLevel ):
		self._batteryLevel = batteryLevel

	def start_travel( self, start_datetime, end_datetime, distance, battery_consumption ):
		new_travel = Travel( self, start_datetime, end_datetime, distance, battery_consumption )
		self._travels.append( new_travel )
		self._is_traveling = True

	def end_travel( self ):
		self._is_traveling = False

	def start_charging_period( self, start_datetime, end_datetime, peak_value ):
		new_charging_period = ChargingPeriod( self, start_datetime, end_datetime, peak_value )
		self._charging_periods.append( new_charging_period )
		self._is_charging = True

	def end_charging_period( self ):
		self._is_charging = False