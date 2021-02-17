import threading
import time

class ChargingPeriod:

	_car = None
	_start_datetime = None
	_end_datetime = None

	def __init__( self, car, start_datetime, end_datetime ):
		self._car = car
		self._start_datetime = start_datetime
		self._end_datetime = end_datetime

		self._charging_period_thread = threading.Thread( target = self.run )
		self._charging_period_thread.start( )		

	def run( self ):
		car = self._car

		simulator = car.get_simulator( )
		sim_sampling_rate = simulator.get_config( 'sim_sampling_rate' )

		charging_period_duration = self._end_datetime - self._start_datetime

		while True:

			simulator.lock_current_datetime( )

			current_datetime = simulator.get_current_datetime( )

			if current_datetime <= self._end_datetime:
				
				car.lock( )	

				elapsed_time = current_datetime - self._start_datetime
				elapsed_time_perc = elapsed_time / charging_period_duration
				elapsed_time_perc_formatted = elapsed_time_perc * 100        									

				charging_period_energy_spent_url = "charging_period/energy_spent/{}".format( elapsed_time_perc )
				charging_period_energy_spent_res = simulator.fetch_gateway( charging_period_energy_spent_url )
				charging_period_energy_spent = float( charging_period_energy_spent_res[ 'charging_period_energy_spent' ] )	
		
				car.set_plug_consumption( charging_period_energy_spent )
				car.log_debug( 'Charging... ({} KW -  {}% of {}%)'.format( charging_period_energy_spent, elapsed_time_perc_formatted, 100 ) )			

				car.unlock( )		
				
				simulator.unlock_current_datetime( )						

			else:

				simulator.unlock_current_datetime( )							
				break
			
			time.sleep( sim_sampling_rate / 1000 )

		car.end_charging_period( )

	def get_car( self ):
		return self._car

	def get_start_datetime( self ):
		return self._start_datetime

	def get_end_datetime( self ):
		return self._end_datetime
