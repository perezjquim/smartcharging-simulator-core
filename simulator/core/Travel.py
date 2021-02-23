import threading
import time
from datetime import date, datetime, timedelta

class Travel:

	_car = None
	_start_datetime = None
	_end_datetime = None
	_distance = 0
	_battery_consumption = 0	
		
	_travel_thread = None

	def __init__( self, car ):
		self._car = car

		self._travel_thread = threading.Thread( target = self.run )
		self._travel_thread.start( )		

	def run( self ):
		car = self._car
		simulator = car.get_simulator( )

		travel_distance_url = "travel/distance"
		travel_distance_res = simulator.fetch_gateway( travel_distance_url )
		self._distance = float( travel_distance_res[ 'travel_distance' ] )

		travel_duration_url = "travel/duration"
		travel_duration_res = simulator.fetch_gateway( travel_duration_url )
		travel_duration = float( travel_duration_res[ 'travel_duration' ] )		

		initial_battery_level = car.get_battery_level( )	
		final_battery_level_url = "travel/final_battery_level/{}/{}".format( initial_battery_level, self._distance )
		final_battery_level_res = simulator.fetch_gateway( final_battery_level_url )
		final_battery_level = int( final_battery_level_res[ 'final_battery_level' ] )

		self._battery_consumption = initial_battery_level - final_battery_level

		simulator.lock_current_datetime( )

		current_datetime = simulator.get_current_datetime( )
		self._start_datetime = current_datetime
		self._end_datetime = self._start_datetime + timedelta( minutes = travel_duration )

		car.log( 'Travel started: designed to go from {} to {}, with a battery consumption of {} and a distance of {} km'.format( self._start_datetime, self._end_datetime, self._battery_consumption, self._distance ) )				

		simulator.unlock_current_datetime( )

		sim_sampling_rate = simulator.get_config( 'sim_sampling_rate' )
		
		while True:

			simulator.lock_current_datetime( )

			current_datetime = simulator.get_current_datetime( )		
			if current_datetime <= self._end_datetime:
				
				car.log_debug( 'Traveling...' )
				simulator.unlock_current_datetime( )				

			else:

				simulator.unlock_current_datetime( )				
				break

			time.sleep( sim_sampling_rate / 1000 )

		car.end_travel( )

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