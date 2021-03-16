import threading
from base.DebugHelper import DebugHelper

class Plug:

	LOG_TEMPLATE = '++++++++++ Plug #{} --- {}'	

	counter = 0

	_id = 0

	_simulator = None
	
	_plugged_car = None
	_charging_periods = [ ]

	_lock = None

	def __init__( self, simulator ):
		Plug.counter += 1
		self._id = Plug.counter
		self._charging_periods = [ ]
		self._simulator = simulator
		self._lock = threading.Lock( )

	def is_busy( self ):
		return self._plugged_car != None

	def plug_car( self, car, charging_period ):
		self._plugged_car = car
		self._charging_periods.append( charging_period )

	def unplug_car( self ):
		self._plugged_car = None

	def get_plugged_car( self ):
		return self._plugged_car

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
		energy_consumption = 0
		if plugged_car:
			plugged_car.lock( )
			plugged_car_id = plugged_car.get_id( )
			energy_consumption = plugged_car.get_plug_consumption( )
			plugged_car.unlock( )

		return {
			'id' : self._id,
			'plugged_car_id' : plugged_car_id,
			'energy_consumption' : energy_consumption,
			"charging_periods" : [ p.get_data( ) for p in self._charging_periods ]
		}
