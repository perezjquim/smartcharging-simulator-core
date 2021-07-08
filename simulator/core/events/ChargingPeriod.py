import time
from datetime import date, datetime, timedelta

from .CarEvent import *

from core.constants.CarConstants import *
from core.objects.Car import *
from core.objects.Plug import *

class ChargingPeriod( CarEvent ):

	_plug = None

	def __init__( self, car = None, plug = None, model_instance = None ):
		super( ).__init__( 'model.events.ChargingPeriodModel', 'ChargingPeriodModel', car, model_instance )		

		self.set_plug( plug )

	def run( self ):
		car = self.get_car( )

		simulation = car.get_simulation( )
		simulator = simulation.get_simulator( )

		car.lock( )
		car.set_status( CarConstants.STATUS_WAITING_TO_CHARGE )
		car.unlock( )

		simulation.acquire_charging_plug( )

		has_found_plug = False

		while not has_found_plug:

			plugs = simulation.get_charging_plugs( )
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

		simulation.lock_current_step( )

		plug = self.get_plug( )			

		if simulation.can_simulate_new_actions( ):

			car.lock( )
			car.set_status( CarConstants.STATUS_CHARGING )
			car.unlock( )					

			charging_period_duration_url = "charging_period/duration"
			charging_period_duration_res = simulation.fetch_gateway( charging_period_duration_url )
			charging_period_duration = float( charging_period_duration_res[ 'charging_period_duration' ] )

			simulation.lock_current_datetime( )

			current_datetime = simulation.get_current_datetime( )

			start_datetime = current_datetime
			self.set_start_datetime( start_datetime )

			end_datetime = start_datetime + timedelta( minutes = charging_period_duration )
			self.set_end_datetime( end_datetime )

			car.log( 'Charging period started: designed to go from {} to {}!'.format( start_datetime, end_datetime ) )				

			simulation.unlock_current_datetime( )				

			simulation.unlock_current_step( )

			sim_sampling_rate = simulator.get_config_by_key( 'sim_sampling_rate' )
			minutes_per_sim_step = simulator.get_config_by_key( 'minutes_per_sim_step' )

			ended_normally = False		
			elapsed_time = 0		

			while simulation.is_simulation_running( ):

				if elapsed_time <= charging_period_duration:					

					plug.lock( )				

					progress_perc = elapsed_time / charging_period_duration
					progress_perc_formatted = progress_perc * 100        					

					if plug.is_enabled( ):									

						elapsed_time = elapsed_time + minutes_per_sim_step
						charging_period_energy_spent_url = "charging_period/energy_spent/{}".format( progress_perc )
						charging_period_energy_spent_res = simulation.fetch_gateway( charging_period_energy_spent_url )
						charging_period_energy_spent = float( charging_period_energy_spent_res[ 'charging_period_energy_spent' ] )

						plug.set_energy_consumption( charging_period_energy_spent )
						car.log_debug( 'Charging... ({} KW - {}% of {}%)'.format( charging_period_energy_spent, progress_perc_formatted, 100 ) )			

					else:

						charging_period_energy_spent = 0							
						plug.set_energy_consumption( charging_period_energy_spent )

						car.log_debug( 'Charging is pending!' )			

					plug.unlock( )

				else:

					ended_normally = True

					break
				
				time.sleep( sim_sampling_rate / 1000 )

			simulation.lock_current_datetime( )
			
			current_datetime = simulation.get_current_datetime( )
			self.set_end_datetime( current_datetime )				

			simulation.unlock_current_datetime( )

			car.end_charging_period( ended_normally )								

		else:

			car.lock( )
			car.log( 'Charging period canceled!' )
			car.set_status( CarConstants.STATUS_READY )
			car.unlock( )					

			simulation.unlock_current_step( )

		plug.release_charging_plug(  )	

	def get_plug( self ):
		return self._plug	

	def set_plug( self, plug ):
		self._plug = plug

		if not self.is_read_only( ):
			model = self.get_model( )		
			plug_model = None	
			if plug:
				plug_model = plug.get_model( )		
			model.set_plug( plug_model )

	def get_data( self ):
		data = super( ).get_data( )
		
		plug_id = ''
		plug_alias = ''

		plug = self.get_plug( )
		if plug:
			plug_id = plug.get_id( )
			plug_alias = plug.get_alias( )

		data.update({
			'plug_id' : plug_id,
			'plug_alias': plug_alias
		})	
		return data		