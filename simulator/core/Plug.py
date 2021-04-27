import threading
from sqlobject import *

from base.DebugHelper import DebugHelper
from .PlugStatuses import PlugStatuses
from data.Logger import Logger
	
class Plug( SQLObject ):

	LOG_TEMPLATE = '++++++++++ Plug {} --- {}'	

	__charging_plugs_semaphore = None		

	_simulator = None
	_status = StringCol( default = PlugStatuses.STATUS_ENABLED, dbName = 'status' )	
	
	_plugged_car = ForeignKey( 'Car', default = None, dbName = 'car_id' )
	_energy_consumption = FloatCol( default = None, dbName = 'energy_consumption' )

	_charging_periods = MultipleJoin( 'ChargingPeriod' )

	_lock = None

	def __init__( self, simulator ):
		super( ).__init__( )

		self._simulator = simulator

		if Plug.__charging_plugs_semaphore == None:
			number_of_charging_plugs = self._simulator.get_config_by_key( 'number_of_charging_plugs' )
			Plug.__charging_plugs_semaphore = threading.Semaphore( number_of_charging_plugs )	

		self._lock = threading.Lock( )

	def acquire_charging_plug( car, charging_period ):
		caller = DebugHelper.get_caller( )		
		Plug.static_log_debug( 'ACQUIRING CHARGING PLUGS SEMAPHORE... (by {})'.format( caller ) )		
		Plug.__charging_plugs_semaphore.acquire( )

	def release_charging_plug( self ):
		self.lock( )
		self.unplug_car( )
		self.unlock( )

		caller = DebugHelper.get_caller( )			
		Plug.static_log_debug( 'RELEASING CHARGING PLUGS SEMAPHORE... (by {})'.format( caller ) )		
		Plug.__charging_plugs_semaphore.release( )		

	def is_available( self ):
		return self.is_enabled( ) and not self.is_busy( )

	def is_enabled( self ):
		return self._status == PlugStatuses.STATUS_ENABLED

	def set_status( self, new_status ):
		self._status = new_status
		self.log( 'New status: {}!'.format( new_status ) )		

	def is_busy( self ):
		car = self.get_plugged_car( )
		return car != None

	def get_id( self ):
		return self.id

	def plug_car( self, car ):
		if self.is_enabled( ):
			self._plugged_car = car

	def unplug_car( self ):
		car = self.get_plugged_car( )
		car.set_plug( None )
		self._plugged_car = None

	def get_plugged_car( self ):
		return self._plugged_car

	def get_energy_consumption( self ):
		return self._energy_consumption

	def set_energy_consumption( self, new_energy_consumption ):
		if self.is_enabled( ):
			self._energy_consumption = new_energy_consumption	
		else:
			self._energy_consumption = 0

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
		Logger.log( Plug.LOG_TEMPLATE.format( self.id, message ) )

	def log_debug( self, message ):
		Logger.log_debug( Plug.LOG_TEMPLATE.format( self.id, message ) )				

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
			'id' : self.id,
			'status' : self._status,
			'plugged_car_id' : plugged_car_id,
			'energy_consumption' : self._energy_consumption,
			"charging_periods" : [ p.get_data( ) for p in self._charging_periods ]
		}		