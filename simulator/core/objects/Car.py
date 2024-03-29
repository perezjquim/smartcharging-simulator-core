import time
import threading
from datetime import timedelta

from .SimulationObject import *

from base.DebugHelper import *
from core.constants.CarConstants import *
from data.Logger import *
from model.objects.CarModel import *

class Car( SimulationObject ):

	LOG_TEMPLATE = '»»»»»»»»»» Car {} --- {}'

	_lock = None

	_travels = [ ]
	_charging_periods = [ ]
	_plug = None

	def __init__( self, simulation = None, model_instance = None ):
		super( ).__init__( 'model.objects.CarModel', 'CarModel', simulation, model_instance )
		
		self._lock = threading.Lock( )

		self._travels = [ ]
		self._charging_periods = [ ]
		self._plug = None

	def get_status( self ):
		model = self.get_model( )
		return model.get_status( )

	def set_status( self, new_status ):
		if not self.is_read_only( ):		
			model = self.get_model( )
			model.set_status( new_status )

	def get_travels( self ):
		return self._travels

	def add_travel( self, new_travel ):
		self._travels.append( new_travel )

	def get_charging_periods( self ):
		return self._charging_periods

	def add_charging_period( self, new_charging_period ):
		self._charging_periods.append( new_charging_period )

	def get_battery_level( self ):
		model = self.get_model( )
		return model.get_battery_level( )

	def set_battery_level( self, battery_level ):
		if not self.is_read_only( ):		
			model = self.get_model( )

			if battery_level >= 0 and battery_level <= 10:
				model.set_battery_level( battery_level )
			elif battery_level < 0:
				model.set_battery_level( 0 )
			elif battery_level > 10:
				model.set_battery_level( 10 )
			else:
				self.log( 'Invalid battery level given!' )

	def get_plug( self ):
		return self._plug

	def set_plug( self, new_plug ):
		self._plug = new_plug	

		if not self.is_read_only( ):		
			model = self.get_model( )

			new_plug_model = None
			if new_plug:
				new_plug_model = new_plug.get_model( )		
				
			model.set_plug( new_plug_model )	

	def lock( self ):
		if not self.is_read_only( ):
			caller = DebugHelper.get_caller( )
			self.log_debug( 'LOCKING... (by {})'.format( caller ) )
			self._lock.acquire( )

	def unlock( self ):
		if not self.is_read_only( ):		
			caller = DebugHelper.get_caller( )
			self.log_debug( 'UNLOCKING... (by {})'.format( caller ) )
			self._lock.release( )

	def is_busy( self ):
		is_busy = self.get_status( ) != CarConstants.STATUS_READY
		return is_busy

	def start_travel( self ):	
		from core.events.Travel import Travel

		new_travel = Travel( self )
		self._travels.append( new_travel )
		self.set_status( CarConstants.STATUS_TRAVELING )

	def end_travel( self ):
		self.lock( )		

		last_travel = self._travels[ -1 ]
		last_travel_battery_consumption = last_travel.get_battery_consumption( )
		battery_level = self.get_battery_level( )
		new_battery_level = battery_level - last_travel_battery_consumption
		self.set_battery_level( new_battery_level )

		self.log( 'Travel ended!' )

		self.unlock( )			

		simulation = self.get_simulation( )
		simulation.lock_current_step( )

		if simulation.can_simulate_new_actions( ) and new_battery_level < 2:

			self.log( 'Car reached <20% battery! Waiting for a available charging plug..' )										
			self._start_charging_period( )		

		else:

			self.lock( )
			self.set_status( CarConstants.STATUS_READY )
			self.unlock( )

		simulation.unlock_current_step( )																				

	def _start_charging_period( self ):
		from core.events.ChargingPeriod import ChargingPeriod

		new_charging_period = ChargingPeriod( self )
		self._charging_periods.append( new_charging_period )

	def end_charging_period( self, ended_normally ):
		self.lock( )	

		plug = self.get_plug( )
		plug.set_energy_consumption( 0 )

		if ended_normally:

			self.set_battery_level( CarConstants.DEFAULT_BATTERY_LEVEL )

		else:

			#TODO
			pass
			
		self.set_status( CarConstants.STATUS_READY )			

		self.log( 'Charging period ended!' )

		self.unlock( )		

	def log( self, message ):
		message_formatted = Car.LOG_TEMPLATE.format( self.get_id( ), message )
		simulation = self.get_simulation( )
		simulation.log( message_formatted )

	def log_debug( self, message ):
		message_formatted = Car.LOG_TEMPLATE.format( self.get_id( ), message )
		simulation = self.get_simulation( )
		simulation.log_debug( message_formatted )	

	def destroy( self ):
		for t in self._travels:
			t.destroy( )

		for c in self._charging_periods:
			c.destroy( )

	def get_alias( self ):
		simulation = self.get_simulation( )
		simulation_cars = simulation.get_cars( )
		alias = 0

		for idx, c in enumerate( simulation_cars ):
			if c.get_id( ) == self.get_id( ):
				alias = idx + 1
				break

		return alias			

	def get_data( self ):
		data = super( ).get_data( )

		plug_id = ''
		plug_consumption = 0
		plug_alias = ''

		plug = self.get_plug( )		
		
		if plug:
			plug_id = plug.get_id( )
			plug_consumption = plug.get_energy_consumption( )
			plug_alias = plug.get_alias( )

		data.update({
			'alias': self.get_alias( ),
			"status" : self.get_status( ),
			"travels" : [ t.get_data( ) for t in self._travels ],
			"charging_periods" : [ p.get_data( ) for p in self._charging_periods ],
			"battery_level" : self.get_battery_level( ),
			"plug_id": plug_id,
			"plug_alias": plug_alias,
			"plug_consumption" : plug_consumption
		})

		return data