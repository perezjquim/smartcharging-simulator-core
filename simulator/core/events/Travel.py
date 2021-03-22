import time
from datetime import date, datetime, timedelta
from .CarEvent import CarEvent

class Travel( CarEvent ):

	counter = 0

	_id = 0
	_distance = 0
	_battery_consumption = 0		

	def __init__( self, car ):
		super( ).__init__( car )

		Travel.counter += 1
		self._id  = Travel.counter

	def run( self ):
		car = self.get_car( )

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

		start_datetime = current_datetime
		self.set_start_datetime( start_datetime )
		
		end_datetime = start_datetime + timedelta( minutes = travel_duration )
		self.set_end_datetime( end_datetime )

		car.log( 'Travel started: designed to go from {} to {}, with a battery consumption of {} and a distance of {} km'.format( start_datetime, end_datetime, self._battery_consumption, self._distance ) )				

		simulator.unlock_current_datetime( )

		sim_sampling_rate = simulator.get_config( 'sim_sampling_rate' )
		
		while simulator.is_simulation_running( ):

			simulator.lock_current_datetime( )

			current_datetime = simulator.get_current_datetime( )		
			if current_datetime <= end_datetime:
				
				car.log_debug( 'Traveling...' )
				simulator.unlock_current_datetime( )				

			else:

				simulator.unlock_current_datetime( )				
				break

			time.sleep( sim_sampling_rate / 1000 )

		car.end_travel( )

	def get_distance( self ):
		return self._distance

	def get_battery_consumption( self ):
		return self._battery_consumption	

	def get_data( self ):
		data = super( ).get_data( )
		data.update({
			'distance' : self._distance,
			'battery_consumption' : self._battery_consumption
		})
		return data