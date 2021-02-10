import threading
import time

class Travel:

	_car = None
	_start_datetime = None
	_end_datetime = None
	_distance = 0
	_battery_consumption = 0	

	_travel_thread = None

	def __init__( self, car, start_datetime, end_datetime, distance, battery_consumption ):
		self._car = car
		self._start_datetime = start_datetime
		self._end_datetime = end_datetime
		self._distance = distance
		self._battery_consumption = battery_consumption

		self._travel_thread = threading.Thread( target = self.run )
		self._travel_thread.start( )		

	def run( self ):
		simulator = self._car.get_simulator( )
		sim_sampling_rate = simulator.get_config( 'sim_sampling_rate' )
		
		while simulator.get_current_datetime( ) <= self._end_datetime:
			self._car.log_debug( 'Traveling...' )
			time.sleep( sim_sampling_rate / 1000 )

		self._car.end_travel( )

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