import time
from datetime import date, datetime, timedelta

from .CarEvent import *

from core.objects.Car import *

class Travel( CarEvent ):

	def __init__( self, car = None, model_instance = None ):
		super( ).__init__( 'model.events.TravelModel', 'TravelModel', car, model_instance )

	def run( self ):
		car = self.get_car( )

		simulation = car.get_simulation( )
		simulator = simulation.get_simulator( )

		travel_distance_url = "travel/distance"
		travel_distance_res = simulation.fetch_gateway( travel_distance_url )
		distance = float( travel_distance_res[ 'travel_distance' ] )
		self.set_distance( distance )

		travel_duration_url = "travel/duration"
		travel_duration_res = simulation.fetch_gateway( travel_duration_url )
		travel_duration = float( travel_duration_res[ 'travel_duration' ] )

		initial_battery_level = car.get_battery_level( )	
		final_battery_level_url = "travel/final_battery_level/{}/{}".format( initial_battery_level, distance )
		final_battery_level_res = simulation.fetch_gateway( final_battery_level_url )
		final_battery_level = float( final_battery_level_res[ 'final_battery_level' ] )

		battery_consumption = initial_battery_level - final_battery_level
		self.set_battery_consumption( battery_consumption )

		simulation.lock_current_datetime( )

		current_datetime = simulation.get_current_datetime( )

		start_datetime = current_datetime
		self.set_start_datetime( start_datetime )
		
		end_datetime = start_datetime + timedelta( minutes = travel_duration )
		self.set_end_datetime( end_datetime )

		car.log( 'Travel started: designed to go from {} to {}, with a battery consumption of {} and a distance of {} km'.format( start_datetime, end_datetime, battery_consumption, distance ) )				

		simulation.unlock_current_datetime( )

		sim_sampling_rate = simulator.get_config_by_key( 'sim_sampling_rate' )
		minutes_per_sim_step = simulator.get_config_by_key( 'minutes_per_sim_step' )

		elapsed_time = 0		
	
		while simulation.is_simulation_running( ):

			if elapsed_time <= travel_duration:

				elapsed_time = elapsed_time + minutes_per_sim_step								
				car.log_debug( 'Traveling...' )		

			else:
		
				break

			time.sleep( sim_sampling_rate / 1000 )

		simulation.lock_current_datetime( )
		
		current_datetime = simulation.get_current_datetime( )
		self.set_end_datetime( current_datetime )				

		simulation.unlock_current_datetime( )			

		car.end_travel( )

	def get_distance( self ):
		model = self.get_model( )
		return model.get_distance( )

	def get_battery_consumption( self ):
		model = self.get_model( )
		return model.get_battery_consumption( )

	def set_distance( self, distance ):
		if not self.is_read_only( ):
			model = self.get_model( )
			model.set_distance( distance )

	def set_battery_consumption( self, battery_consumption ):
		if not self.is_read_only( ):		
			model = self.get_model( )
			model.set_battery_consumption( battery_consumption )		

	def get_data( self ):
		data = super( ).get_data( )
		data.update({
			'distance' : self.get_distance( ),
			'battery_consumption' : self.get_battery_consumption( )
		})
		return data