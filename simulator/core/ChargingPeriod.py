import threading
import time

class ChargingPeriod:

	_car = None
	_start_datetime = None
	_end_datetime = None
	_peak_value = 0

	def __init__( self, car, start_datetime, end_datetime, peak_value ):
		self._car = car
		self._start_datetime = start_datetime
		self._end_datetime = end_datetime
		self._peak_value = peak_value

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

				# <= 50% carregamento feito
				# (2 * perc * peak)
				# ex.: 2 * 0.3 * 2800
				# ex.: 2 * 0.5 * 2800
				if elapsed_time_perc <= 0.5: 
					plug_consumption = ( 2 * elapsed_time_perc ) * self._peak_value

				# > 50% carregamento feito
				# ( 1 - perc ) * peak
				# ex.: ( 1 - 0.8 ) * 2800
				else:
					plug_consumption = elapsed_time_perc * self._peak_value

				elapsed_time_perc_formatted = elapsed_time_perc * 100
		
				car.set_plug_consumption( plug_consumption )
				car.log_debug( 'Charging... ({} KW -  {}% of {}%)'.format( plug_consumption, elapsed_time_perc_formatted, 100 ) )			

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

	def get_peak_value( self ):
		return self._peak_value		
