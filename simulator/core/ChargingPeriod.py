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
		simulator = self._car.get_simulator( )
		sim_sampling_rate = simulator.get_config( 'sim_sampling_rate' )
		
		while True:
			current_datetime = simulator.get_current_datetime( )
			if current_datetime >= self._end_datetime:	
				self._car.end_charging_period( )
				break

			time.sleep( sim_sampling_rate / 1000 )

	def get_car( self ):
		return self._car

	def get_start_datetime( self ):
		return self._start_datetime

	def get_end_datetime( self ):
		return self._end_datetime

	def get_peak_value( self ):
		return self._peak_value		
