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

	def reset_counter( ):
		ChargingPeriod.__counter = 0		

	def run( self ):
		car = self.get_car( )

		simulator = car.get_simulator( )

		car.lock( )
		car.set_status( CarStatuses.STATUS_WAITING_TO_CHARGE )
		car.unlock( )

		Plug.acquire_charging_plug( car, self )

		has_found_plug = False

		while not has_found_plug:

			plugs = simulator.get_charging_plugs( )
			for p in plugs:
				p.lock( )

				if p.is_available( ):
					
					has_found_plug = True
					p.plug_car( car )
					p.add_charging_period( self )				
					car.set_plug( p )
					self.set_plug( p )									

					p.unlock( )
					break

				p.unlock( )		

		simulator.lock_current_step( )

		if simulator.can_simulate_new_actions( ):

			car.lock( )
			car.set_status( CarStatuses.STATUS_CHARGING )
			car.unlock( )					

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
			minutes_per_sim_step = simulator.get_config( 'minutes_per_sim_step' )

			ended_normally = False		
			elapsed_time = 0			

			while simulator.is_simulation_running( ):

				if elapsed_time <= charging_period_duration:					

					self._plug.lock( )				

					progress_perc = elapsed_time / charging_period_duration
					progress_perc_formatted = progress_perc * 100        					

					if self._plug.is_enabled( ):									

						elapsed_time = elapsed_time + minutes_per_sim_step
						charging_period_energy_spent_url = "charging_period/energy_spent/{}".format( progress_perc )
						charging_period_energy_spent_res = simulator.fetch_gateway( charging_period_energy_spent_url )
						charging_period_energy_spent = float( charging_period_energy_spent_res[ 'charging_period_energy_spent' ] )	

						self._plug.set_energy_consumption( charging_period_energy_spent )
						car.log_debug( 'Charging... ({} KW - {}% of {}%)'.format( charging_period_energy_spent, progress_perc_formatted, 100 ) )			

					else:

						charging_period_energy_spent = 0							
						self._plug.set_energy_consumption( charging_period_energy_spent )

						car.log_debug( 'Charging is pending!' )			

					self._plug.unlock( )

				else:

					ended_normally = True

					break
				
				time.sleep( sim_sampling_rate / 1000 )

			simulator.lock_current_datetime( )
			
			current_datetime = simulator.get_current_datetime( )
			self.set_end_datetime( current_datetime )				

			simulator.unlock_current_datetime( )

			car.end_charging_period( ended_normally )								

		else:

			car.lock( )
			car.log( 'Charging period canceled!' )
			car.set_status( CarStatuses.STATUS_READY )
			car.unlock( )					

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