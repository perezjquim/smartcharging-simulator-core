import time
from datetime import date, datetime, timedelta
from .CarEvent import CarEvent
from core.CarStatuses import CarStatuses
from core.Plug import Plug

class ChargingPeriod( CarEvent ):

	__counter = 0

	_id = 0	

	_plug = None

	def __init__( self, car ):
		super( ).__init__( car )	

		ChargingPeriod.__counter += 1
		self._id = ChargingPeriod.__counter

	def run( self ):
		car = self.get_car( )

		simulator = car.get_simulator( )

		car.lock( )
		car.set_status( CarStatuses.STATUS_WAITING_TO_CHARGE )
		car.unlock( )

		Plug.acquire_charging_plug( car, self )

		plugs = simulator.get_charging_plugs( )
		for p in plugs:
			p.lock( )

			if not p.is_available( ):
				p.plug_car( car )
				p.add_charging_period( self )
				self.set_plug( p )				
				
				p.unlock( )
				break

			p.unlock( )		

		car.lock( )
		car.set_status( CarStatuses.STATUS_CHARGING )
		car.unlock( )		

		simulator.lock_current_step( )

		if simulator.can_simulate_new_actions( ):

			charging_period_duration_url = "charging_period/duration"
			charging_period_duration_res = simulator.fetch_gateway( charging_period_duration_url )
			charging_period_duration = float( charging_period_duration_res[ 'charging_period_duration' ] )

			simulator.lock_current_datetime( )

			current_datetime = simulator.get_current_datetime( )

			start_datetime = current_datetime
			self.set_start_datetime( start_datetime )

			end_datetime = start_datetime + timedelta( minutes = charging_period_duration )
			self.set_end_datetime( end_datetime )

			car.log( 'Charging period started: designed to go from {} to {}!'.format( start_datetime, end_datetime ) )				

			simulator.unlock_current_datetime( )				

			simulator.unlock_current_step( )

			sim_sampling_rate = simulator.get_config( 'sim_sampling_rate' )

			ended_normally = False					

			while simulator.is_simulation_running( ):

				simulator.lock_current_datetime( )

				current_datetime = simulator.get_current_datetime( )

				if current_datetime <= end_datetime:
					
					car.lock( )	

					self._plug.lock( )

					charging_period_energy_spent = 0					

					if self._plug.is_enabled( ):

						elapsed_time = ( ( current_datetime - start_datetime ).total_seconds( ) ) / 60
						elapsed_time_perc = elapsed_time / charging_period_duration
						elapsed_time_perc_formatted = elapsed_time_perc * 100        									

						charging_period_energy_spent_url = "charging_period/energy_spent/{}".format( elapsed_time_perc )
						charging_period_energy_spent_res = simulator.fetch_gateway( charging_period_energy_spent_url )
						charging_period_energy_spent = float( charging_period_energy_spent_res[ 'charging_period_energy_spent' ] )	

					self._plug.set_energy_consumption( charging_period_energy_spent )

					self._plug.unlock( )

					car.log_debug( 'Charging... ({} KW - {}% of {}%)'.format( charging_period_energy_spent, elapsed_time_perc_formatted, 100 ) )			

					car.unlock( )		
					
					simulator.unlock_current_datetime( )						

				else:

					ended_normally = True

					simulator.unlock_current_datetime( )

					break
				
				time.sleep( sim_sampling_rate / 1000 )

			car.end_charging_period( ended_normally )								

		else:

			simulator.unlock_current_step( )

		self._plug.release_charging_plug(  )		

	def set_plug( self, new_plug ):
		self._plug = new_plug	

	def get_data( self ):
		data = super( ).get_data( )
		
		plug_id = ''
		if self._plug:
			plug_id = self._plug.get_id( )

		data.update({
			'plug_id' : plug_id
		})	
		return data		