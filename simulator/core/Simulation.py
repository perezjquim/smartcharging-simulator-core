import threading
import time
import requests
from datetime import date, datetime, timedelta
import traceback as tb

from base.BaseModelProxy import *

from stats.StatsHelper import *
from data.Logger import *
from base.DebugHelper import *
from .objects.Car import *
from .objects.Plug import *
from .objects.Log import *
from .events.Travel import *
from .events.ChargingPeriod import *
from model.SimulationModel import *
from data.WebhookHelper import *

class Simulation( BaseModelProxy ):

	MAIN_LOG_PREFIX = '============================'

	__GATEWAY_TIMEOUT = 3

	_cars = [ ]
	_charging_plugs = [ ]
	_logs = [ ]

	_affluence_counts = { }

	_charging_plugs_semaphore = None

	_current_step = 1
	_current_step_lock = None

	_current_datetime = None	
	_current_datetime_lock = None

	_is_simulation_running = False
	_is_simulation_running_lock = None		

	_simulator = None	
	_thread = None	

	_stats_helper = None

	def __init__( self, simulator = None, model_instance = None ):
		super( ).__init__( 'model.SimulationModel', 'SimulationModel', model_instance )	

		self._cars = [ ]
		self._charging_plugs = [ ]
		self._logs = [ ]

		self._affluence_counts = { }

		self._charging_plugs_semaphore = None

		self._current_step = 1
		self._current_step_lock = threading.Lock( )

		self._current_datetime = None
		self._current_datetime_lock = threading.Lock( )

		self._is_simulation_running = False
		self._is_simulation_running_lock = threading.Lock( )

		self._simulator = simulator		

		self._thread = threading.Thread( target = self.run )		

		self._stats_helper = StatsHelper( self )	

		simulation_id = self.get_id( )
		current_datetime = datetime.now( )	
		description = 'Simulation #{} - {}'.format( simulation_id, current_datetime )
		self.set_description( description )			

	def get_simulator( self ):
		return self._simulator

	def get_description( self ):
		model = self.get_model( )
		return model.get_description( )

	def set_description( self, description ):
		if not self.is_read_only( ):		
			model = self.get_model( )
			return model.set_description( description )

	def on_start( self ):
		self.initialize_cars( )
		self.initialize_plugs( )
		self.initialize_datetime( )

		self.set_simulation_state( True )		
						
		self._thread.start( )	

		WebhookHelper.send_message( 'Simulation started!', 'INFO' )		

	def initialize_cars( self ):
		self.log( 'Initializing cars...' )

		simulator = self._simulator
		number_of_cars = simulator.get_config_by_key( 'number_of_cars' )
		for n in range( number_of_cars ):
			self._cars.append( Car( self ) )

		self.log( 'Initializing cars... done!' )

	def initialize_datetime( self ):
		self.log( 'Initializing date...' )

		today_date = date.today( )
		today_year = today_date.year
		today_month = today_date.month
		today_day = today_date.day

		self.set_current_datetime( datetime( year = today_year, month = today_month, day = today_day ) )
		self.log( 'Date initialized as: {}'.format( self._current_datetime ) )

		self.log( 'Initializing date... done!' )

	def initialize_plugs( self ):
		self.log( 'Initializing plugs...' )

		simulator = self._simulator
		number_of_charging_plugs = simulator.get_config_by_key( 'number_of_charging_plugs' )
		for n in range( number_of_charging_plugs ):
			self._charging_plugs.append( Plug( self ) )

		self._charging_plugs_semaphore = threading.Semaphore( number_of_charging_plugs )							

		self.log( 'Initializing plugs... done!' )									

	def on_stop( self ):			
		self._end_simulation( True )	

		WebhookHelper.send_message( 'Simulation stopped!', 'INFO' )

	def run( self ):
		self.log_main( 'Simulating...' )		

		simulator = self._simulator

		sim_sampling_rate = simulator.get_config_by_key( 'sim_sampling_rate' )		
		number_of_steps = simulator.get_config_by_key( 'number_of_steps' )

		while self.is_simulation_running( ):

			number_of_busy_cars = 0
			total_plug_consumption = 0

			for c in self._cars:
				c.lock( )

				if c.is_busy( ):
					number_of_busy_cars += 1

				car_plug = c.get_plug( )
				if car_plug:
					plug_energy_consumption = car_plug.get_energy_consumption( )
					total_plug_consumption += plug_energy_consumption

				c.unlock( )		

			self.log( '### TOTAL PLUG CONSUMPTION: {} KW ###'.format( total_plug_consumption ) )

			should_simulate_next_step = ( self.can_simulate_new_actions( ) or number_of_busy_cars > 0 )

			if should_simulate_next_step:	

				self.log( "> Simulation step..." )		

				self.lock_current_datetime( )

				current_datetime = self.get_current_datetime( )
				current_step = self.get_current_step( )				
				if current_step > 1:
					
					minutes_per_sim_step = simulator.get_config_by_key( 'minutes_per_sim_step' )
					current_datetime += timedelta( minutes = minutes_per_sim_step )
					self.set_current_datetime( current_datetime )	

				self.unlock_current_datetime( )
				
				self.log( "( ( ( Step #{} - at: {} ) ) )".format( current_step, current_datetime ) )						

				self.on_step( current_datetime )

				self.lock_current_step( )
				
				current_step += 1
				self.set_current_step( current_step )			

				self.unlock_current_step( )

				self.log( '< Simulation step... done!' )							

			else:

				self._end_simulation( False )		

				WebhookHelper.send_message( 'Simulation ended!', 'INFO' )					

			simulator.send_sim_data_to_clients( )

			time.sleep( sim_sampling_rate / 1000 )	
							
		self.log_main( 'Simulating... done!' )

	def on_step( self, current_datetime ):

		if self.can_simulate_new_actions( ):

			current_datetime_str = current_datetime.strftime( '%Y%m%d%H' )

			if current_datetime_str in self._affluence_counts:

				pass
			
			else:

				current_hour_of_day = current_datetime.hour
				affluence_url = "travel/affluence/{}".format( current_hour_of_day )
				affluence_res = self.fetch_gateway( affluence_url )
				affluence = int( affluence_res[ 'affluence' ] )
				self._affluence_counts[ current_datetime_str ] = affluence	

			if self._affluence_counts[ current_datetime_str ] > 0:		

				simulator = self._simulator

				for c in self._cars:

					c.lock( )

					car_can_travel = ( self.is_simulation_running( ) and not c.is_busy( ) )		
					if car_can_travel:
						c.start_travel( )	
						self._affluence_counts[ current_datetime_str ] -= 1	

					c.unlock( )

					if self._affluence_counts[ current_datetime_str ] < 1:						
						break					

		else:
			
			self.log( '-- Simulation period ended: this step is only used to resume travels and/or charging periods! --' )

	def can_simulate_new_actions( self ):
		simulator = self._simulator
		number_of_steps = simulator.get_config_by_key( 'number_of_steps' )
		can_simulate_new_actions = self.is_simulation_running( ) and ( self._current_step <= number_of_steps )
		return can_simulate_new_actions

	def lock_current_datetime( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'LOCKING DATETIME... (by {})'.format( caller ) )
		self._current_datetime_lock.acquire( )

	def unlock_current_datetime( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'UNLOCKING DATETIME... (by {})'.format( caller ) )
		self._current_datetime_lock.release( )

	def lock_current_step( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'LOCKING STEP... (by {})'.format( caller ) )
		self._current_step_lock.acquire( )

	def unlock_current_step( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'UNLOCKING STEP... (by {})'.format( caller ) )
		self._current_step_lock.release( )		

	def get_current_datetime( self ):
		return self._current_datetime

	def set_current_datetime( self, new_datetime ):
		if not self.is_read_only( ):		
			self._current_datetime = 	new_datetime

	def get_current_step( self ):
		return self._current_step

	def set_current_step( self, new_step ):
		if not self.is_read_only( ):		
			self._current_step = new_step				

	def _end_simulation( self, wait_for_thread ):	
		self.set_simulation_state( False )

		for c in self._cars:
			c.destroy( )	

		if wait_for_thread:					
			self._thread.join( )

		simulator = self._simulator
		simulator.send_sim_data_to_clients( )

	def log( self, message ):
		new_log = Log( self, message )
		self._logs.append( new_log )
		print( message )		

	def log_main( self, message ):
		self.log( '{} {}'.format( Simulation.MAIN_LOG_PREFIX, message ) ) 

	def log_debug( self, message ):
		simulator = self._simulator
		is_debug_enabled = simulator.get_config_by_key( 'enable_debug_mode' )
		if is_debug_enabled:
			self.log( message )

	def get_cars( self ):
		return self._cars

	def get_charging_plugs( self ):
		return self._charging_plugs

	def get_logs( self ):
		return self._logs

	def set_charging_plug_status( self, plug_id, plug_new_status ):
		if not self.is_read_only( ):		
			plug = list( filter( lambda p : p.get_id( ) == plug_id, self._charging_plugs ) )
			plug = plug[ 0 ]
			plug.lock( )
			plug.set_status( plug_new_status )
			plug.unlock( )		

	def acquire_charging_plug( self ):
		caller = DebugHelper.get_caller( )		
		self.log_debug( 'ACQUIRING CHARGING PLUGS SEMAPHORE... (by {})'.format( caller ) )		
		self._charging_plugs_semaphore.acquire( )		

	def release_charging_plug( self ):
		caller = DebugHelper.get_caller( )			
		self.log_debug( 'RELEASING CHARGING PLUGS SEMAPHORE... (by {})'.format( caller ) )		
		self._charging_plugs_semaphore.release( )	

	def lock_simulation( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'LOCKING SIMULATION... (by {})'.format( caller ) )
		self._is_simulation_running_lock.acquire( )		

	def unlock_simulation( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'UNLOCKING SIMULATION... (by {})'.format( caller ) )
		self._is_simulation_running_lock.release( )			

	def is_simulation_running( self ):
		self.lock_simulation( )
		is_simulation_running = self._is_simulation_running
		self.unlock_simulation( )
		return is_simulation_running

	def set_simulation_state( self, new_value ):
		if not self.is_read_only( ):		
			self.lock_simulation( )
			self._is_simulation_running = new_value
			self.unlock_simulation( )

			simulator = self._simulator
			simulator.send_sim_state_to_clients( )			

	def fetch_gateway( self, endpoint ):
		simulator = self._simulator

		base_url = simulator.get_config_by_key( 'gateway_request_base_url' )
		url = base_url.format( endpoint )
		self.log_debug( '\\\\\\ GATEWAY \\\\\\ URL: {}'.format( url )	 )	

		response = requests.get( url, timeout = Simulation.__GATEWAY_TIMEOUT )
		response_json = response.json( )
		self.log_debug( '\\\\\\ GATEWAY \\\\\\ RESPONSE: {}'.format( response_json ) )			

		return response_json		

	def get_plugs_data( self ):

		plugs_sim_data = [ ]				

		plugs = self.get_charging_plugs( )

		for p in plugs:
			p.lock( )

			plug_data = p.get_data( )
			plugs_sim_data.append( plug_data )

			p.unlock( )

		plugs_sim_data.sort( key = lambda x : x[ 'id' ] )

		return plugs_sim_data

	def get_cars_data( self ):

		cars_sim_data = [ ]

		cars = self.get_cars( )

		for c in cars:
			c.lock( )
			
			car_data = c.get_data( )
			cars_sim_data.append( car_data )

			c.unlock( )

		cars_sim_data.sort( key = lambda x : x[ 'id' ] )

		return cars_sim_data			
	
	def get_travel_data( self ):

		travels_sim_data = [ ]

		cars = self.get_cars( )

		for c in cars:
			c.lock( )
			
			car_data = c.get_data( )

			travel_data = car_data[ 'travels' ]
			travels_sim_data += travel_data	

			c.unlock( )

		travels_sim_data.sort( key = lambda x : x[ 'id' ] )			

		return travels_sim_data

	def get_charging_period_data( self ):

		charging_periods_sim_data = [ ]

		cars = self.get_cars( )

		for c in cars:
			c.lock( )
			
			car_data = c.get_data( )

			charging_period_data = car_data[ 'charging_periods' ]
			charging_periods_sim_data += charging_period_data		

			c.unlock( )	
			
		charging_periods_sim_data.sort( key = lambda x : x[ 'id' ] )	
		
		return charging_periods_sim_data	

	def get_logs_data( self ):
		logs_sim_data = [ ]

		logs = self.get_logs( )

		for l in logs:
			log_data = l.get_data( )
			logs_sim_data.append( log_data )
			
		logs_sim_data.sort( key = lambda x : x[ 'id' ] )	
		
		return logs_sim_data			

	def get_simulation_stats( self ):
		stats_helper = self._stats_helper
		return stats_helper.get_data( )	

	def update_simulation_stats( self, simulation_data ):
		stats_helper = self._stats_helper
		stats_helper.update_stats( simulation_data )			

	def get_simulation_data( self ):	
		cars_sim_data = self.get_cars_data( )
		travels_sim_data = self.get_travel_data( )
		charging_periods_sim_data = self.get_charging_period_data( )
		plugs_sim_data = self.get_plugs_data( )
		logs_sim_data = self.get_logs_data( )	

		sim_datetime = self.get_current_datetime( )
		sim_datetime_str = '' 
		if sim_datetime:
			sim_datetime_str = sim_datetime.isoformat( )

		simulation_data = {
			'sim_datetime': sim_datetime_str,
			'cars': cars_sim_data, 
			'travels': travels_sim_data, 
			'charging_periods': charging_periods_sim_data,
			'plugs': plugs_sim_data,
			'logs': logs_sim_data
		}		

		if not self.is_read_only( ):
			self.update_simulation_stats( simulation_data )

		simulation_stats = self.get_simulation_stats( )
		simulation_data.update( simulation_stats )	

		return simulation_data

	def add_car( self, car ):
		self._cars.append( car )

	def add_charging_plug( self, charging_plug ):
		self._charging_plugs.append( charging_plug )

	def add_log( self, log ):
		self._logs.append( log )

	def set_stat( self, stat_type, stat ):
		self._stats_helper.set_stat( stat_type, stat )

	def get_by_id( simulation_id ):
		simulation_model = SimulationModel.get( simulation_id )
		simulation = Simulation( model_instance = simulation_model )

		car_models = simulation_model.get_cars( )
		for cm in car_models:
			car = Car( model_instance = cm, simulation = simulation )

			plug_model = cm.get_plug( )
			if plug_model:
				plug = Plug( model_instance = plug_model )
				car.set_plug( plug )			
			
			travel_models = cm.get_travels( )
			for tm in travel_models:
				travel = Travel( model_instance = tm, car = car )
				car.add_travel( travel )

			charging_period_models = cm.get_charging_periods( )
			for cpm in charging_period_models:
				plug_model_of_cpm = cpm.get_plug( )
				plug_of_cpm = Plug( model_instance = plug_model_of_cpm )
				charging_period = ChargingPeriod( model_instance = cpm, car = car, plug = plug_of_cpm )
				car.add_charging_period( charging_period )

			simulation.add_car( car )

		charging_plug_models = simulation_model.get_charging_plugs( )
		for pm in charging_plug_models:
			plug = Plug( model_instance = pm, simulation = simulation )

			plugged_car_model = pm.get_plugged_car( )
			if plugged_car_model:
				plugged_car = Car( model_instance = plugged_car_model )			
				plug.set_plugged_car( plugged_car )			

			charging_period_models = pm.get_charging_periods( )
			for cpm in charging_period_models:
				charging_period = ChargingPeriod( model_instance = cpm, plug = plug )
				plug.add_charging_period( charging_period )			

			simulation.add_charging_plug( plug )	

		log_models = simulation_model.get_logs( )
		for lm in log_models:
			log = Log( model_instance = lm, simulation = simulation )

			simulation.add_log( log )

		stat_models = simulation_model.get_stats( )
		for sm in stat_models:
			stat = Stat( model_instance = sm, simulation = simulation )

			stat_type = stat.get_type( )
			simulation.set_stat( stat_type, stat )

		return simulation

	def get_data_by_id( simulation_id ):
		simulation = Simulation.get_by_id( simulation_id )
		return simulation.get_simulation_data( )

	def get_sim_list( current_simulation ):
		simulations = SimulationModel.select( )
		sim_list = [ ]

		for s in simulations:
			is_running = ( current_simulation and current_simulation.get_id( ) == s.get_id( ) and current_simulation.is_simulation_running( ) )
			sim_list.append({
				'id': s.get_id( ),
				'is_running': is_running,
				'description': s.get_description( )
			})

		return sim_list