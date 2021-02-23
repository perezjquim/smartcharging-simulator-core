import threading
import time
from datetime import date, datetime, timedelta

class ChargingPeriod:

	_car = None
	_duration = 0
	_start_datetime = None
	_end_datetime = None

	def __init__( self, car ):
		self._car = car

		self._charging_period_thread = threading.Thread( target = self.run )
		self._charging_period_thread.start( )		

	def run( self ):
		car = self._car

		simulator = car.get_simulator( )

		simulator.acquire_charging_plugs_semaphore( )

		simulator.lock_current_step( )

		if simulator.can_simulate_new_actions( ):

			charging_period_duration_url = "charging_period/duration"
			charging_period_duration_res = simulator.fetch_gateway( charging_period_duration_url )
			charging_period_duration = float( charging_period_duration_res[ 'charging_period_duration' ] )

			simulator.lock_current_datetime( )

			current_datetime = simulator.get_current_datetime( )
			self._start_datetime = current_datetime
			self._end_datetime = self._start_datetime + timedelta( minutes = charging_period_duration )

			car.log( 'Charging period started: designed to go from {} to {}!'.format( self._start_datetime, self._end_datetime ) )				

			simulator.unlock_current_datetime( )				

			simulator.unlock_current_step( )

			sim_sampling_rate = simulator.get_config( 'sim_sampling_rate' )

			while True:

				simulator.lock_current_datetime( )

				current_datetime = simulator.get_current_datetime( )

				if current_datetime <= self._end_datetime:
					
					car.lock( )	

					elapsed_time = ( ( current_datetime - self._start_datetime ).total_seconds( ) ) / 60
					elapsed_time_perc = elapsed_time / charging_period_duration
					elapsed_time_perc_formatted = elapsed_time_perc * 100        									

					charging_period_energy_spent_url = "charging_period/energy_spent/{}".format( elapsed_time_perc )
					charging_period_energy_spent_res = simulator.fetch_gateway( charging_period_energy_spent_url )
					charging_period_energy_spent = float( charging_period_energy_spent_res[ 'charging_period_energy_spent' ] )	
			
					car.set_plug_consumption( charging_period_energy_spent )
					car.log_debug( 'Charging... ({} KW - {}% of {}%)'.format( charging_period_energy_spent, elapsed_time_perc_formatted, 100 ) )			

					car.unlock( )		
					
					simulator.unlock_current_datetime( )						

				else:

					simulator.unlock_current_datetime( )							
					break
				
				time.sleep( sim_sampling_rate / 1000 )

			car.end_charging_period( )								

		else:

			simulator.unlock_current_step( )

		simulator.release_charging_plugs_semaphore( )			

	def get_car( self ):
		return self._car

	def get_start_datetime( self ):
		return self._start_datetime

	def get_end_datetime( self ):
		return self._end_datetime
