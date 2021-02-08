import time
import threading
from datetime import timedelta
from .Travel import Travel
from .ChargingPeriod import ChargingPeriod

class Car:

	DEFAULT_BATTERY_LEVEL = 10

	_simulator = None
	_is_traveling = False
	_is_charging = False
	_travels = [ ]
	_charging_periods = [ ]
	_battery_level = 0
	_car_lock = None

	def __init__( self, simulator ):
		self._simulator = simulator
		self._is_traveling = False
		self._is_charging = False
		self._travels = [ ]	
		self._charging_periods = [ ]
		self._battery_level = Car.DEFAULT_BATTERY_LEVEL		
		self._car_lock = threading.Lock( )

	def get_simulator( self ):
		return self._simulator

	def is_traveling( self ):
		with self._car_lock:
			return self._is_traveling

	def is_charging( self ):
		with self._car_lock:
			return self._is_charging

	def set_charging_state( self, new_charging_state ):
		with self._car_lock:
			self._is_charging = new_charging_state

	def set_traveling_state( self, new_traveling_state ):
		with self._car_lock:
			self._is_traveling = new_traveling_state			

	def get_travels( self ):
		with self._car_lock:
			return self._travels

	def get_charging_periods( self ):
		with self._car_lock:
			return self._charging_periods

	def get_battery_level( self ):
		return self._battery_level

	def set_battery_level( self, battery_level ):
		if battery_level >= 0 and battery_level <= 10:
			self._battery_level = battery_level
		else:
			self._simulator.log( 'Invalid battery level given!' )

	def start_travel( self, start_datetime, end_datetime, distance, battery_consumption ):
		if self.is_traveling( ):
			self._simulator.log( 'Car was traveling, yet an attempt to start a travel was made (??)' )
		else:
			new_travel = Travel( self, start_datetime, end_datetime, distance, battery_consumption )
			self._travels.append( new_travel )
			self._is_traveling = True
			print( 'Travel started: designed to go from {} to {}'.format( start_datetime, end_datetime ) )

	def end_travel( self ):
		if self.is_traveling( ):
			self._is_traveling = False
			print( 'Travel ended!' )
		else:
			self._simulator.log( 'Car was not traveling, yet an attempt to end a travel was made (??)' )

	def start_charging_period( self, start_datetime, end_datetime, peak_value ):
		if self.is_charging( ):
			self._simulator.log( 'Car was charging, yet an attempt to start a charging period was made (??)' )
		else:
			new_charging_period = ChargingPeriod( self, start_datetime, end_datetime, peak_value )
			self._charging_periods.append( new_charging_period )
			self._is_charging = True
			print( 'Charging period started: designed to go from {} to {}'.format( start_datetime, end_datetime ) )

	def end_charging_period( self ):
		if self.is_charging( ):
			self._is_charging = False
			print( 'Charging period ended!' )
		else:
			self._simulator.log( 'Car was not charging, yet an attempt to end a charging period was made (??)' )