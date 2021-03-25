import threading
from base.DebugHelper import DebugHelper

class Plug:

	LOG_TEMPLATE = '++++++++++ Plug #{} --- {}'	

	counter = 0

	_id = 0

	_simulator = None
	
	_plugged_car = None
	_energy_consumption = 0

	_charging_periods = [ ]

	_lock = None

	def __init__( self, simulator ):
		Plug.counter += 1
		self._id = Plug.counter
		self._charging_periods = [ ]
		self._simulator = simulator
		self._energy_consumption = 0		
		self._lock = threading.Lock( )

	def is_busy( self ):
		return self._plugged_car != None

	def get_id( self ):
		return self._id

	def plug_car( self, car ):
		car.set_plug( self )
		self._plugged_car = car

	def unplug_car( self ):
		self._plugged_car.set_plug( None )
		self._plugged_car = None

	def get_plugged_car( self ):
		return self._plugged_car

	def get_energy_consumption( self ):
		return self._energy_consumption

	def set_energy_consumption( self, new_energy_consumption ):
		self._energy_consumption = new_energy_consumption	

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

	def log( self, message ):
		self._simulator.log( Plug.LOG_TEMPLATE.format( self._id, message ) )

	def log_debug( self, message ):
		self._simulator.log_debug( Plug.LOG_TEMPLATE.format( self._id, message ) )				

	def destroy( self ):
		#NOP
		pass

	def get_data( self ):
		plugged_car = self._plugged_car
		plugged_car_id = ''
		if plugged_car:
			plugged_car.lock( )
			plugged_car_id = plugged_car.get_id( )
			plugged_car.unlock( )

		return {
			'id' : self._id,
			'plugged_car_id' : plugged_car_id,
			'energy_consumption' : self._energy_consumption,
			"charging_periods" : [ p.get_data( ) for p in self._charging_periods ]
		}
