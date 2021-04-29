import threading

from .SimulationObject import *

from base.DebugHelper import *
from core.constants.PlugConstants import *
from data.Logger import *

from model.objects.PlugModel import *
	
class Plug( SimulationObject ):

	LOG_TEMPLATE = '++++++++++ Plug {} --- {}'	

	_plugged_car = None
	_charging_periods = [ ]

	_lock = None

	def __init__( self, simulation ):
		super( ).__init__( 'model.objects.PlugModel', 'PlugModel', simulation )

		self._lock = threading.Lock( )

	def get_status( self ):
		model = self.get_model( )
		return model.get_status( )

	def set_status( self, new_status ):
		model = self.get_model( )
		model.set_status( new_status )

	def acquire_charging_plug( ):
		simulation = self.get_simulation( )
		simulation.acquire_charging_plug( )

	def release_charging_plug( self ):
		self.lock( )
		self.unplug_car( )
		self.unlock( )

		simulation = self.get_simulation( )
		simulation.release_charging_plug( )

	def is_available( self ):
		return self.is_enabled( ) and not self.is_busy( )

	def is_enabled( self ):
		return self.get_status( ) == PlugConstants.STATUS_ENABLED	

	def is_busy( self ):
		car = self.get_plugged_car( )
		return car != None

	def plug_car( self, car ):
		if self.is_enabled( ):
			self.set_plugged_car( car )

	def unplug_car( self ):
		car = self.get_plugged_car( )
		car.set_plug( None )
		self.set_plugged_car( None )

	def get_plugged_car( self ):
		return self._plugged_car

	def set_plugged_car( self, car ):
		self._plugged_car = car
		plugged_car_model = plugged_car.get_model( )

		model = self.get_model( )
		model.set_plugged_car( plugged_car_model )

	def get_energy_consumption( self ):
		model = self.get_model( )
		return model.get_energy_consumption( )

	def set_energy_consumption( self, new_energy_consumption ):
		model = self.get_model( )

		if self.is_enabled( ):
			model.set_energy_consumption( new_energy_consumption	)
		else:
			model.set_energy_consumption( 0	 )

	def add_charging_period( self, new_charging_period ):
		self._charging_periods.append( new_charging_period )		

	def get_charging_periods( self ):
		return self._charging_periods

	def lock( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'LOCKING... (by {})'.format( caller ) )
		self._lock.acquire( )

	def unlock( self ):
		caller = DebugHelper.get_caller( )
		self.log_debug( 'UNLOCKING... (by {})'.format( caller ) )
		self._lock.release( )		

	def static_log( message ):
		Logger.log( Plug.LOG_TEMPLATE.format( '', message ) )

	def static_log_debug( message ):
		Logger.log_debug( Plug.LOG_TEMPLATE.format( '', message ) )	

	def log( self, message ):
		Logger.log( Plug.LOG_TEMPLATE.format( self.get_id( ), message ) )

	def log_debug( self, message ):
		Logger.log_debug( Plug.LOG_TEMPLATE.format( self.get_id( ), message ) )				

	def destroy( self ):
		#NOP
		pass

	def get_data( self ):
		plugged_car = self.get_plugged_car( )
		plugged_car_id = ''
		if plugged_car:
			plugged_car.lock( )
			plugged_car_id = plugged_car.get_id( )
			plugged_car.unlock( )

		return {
			'id' : self.get_id( ),
			'status' : self._status,
			'plugged_car_id' : plugged_car_id,
			'energy_consumption' : self._energy_consumption,
			"charging_periods" : [ p.get_data( ) for p in self._charging_periods ]
		}		