from base.SingletonMetaClass import SingletonMetaClass

class StatsHelper( metaclass = SingletonMetaClass ):

	_car_stats = [ ]
	_travel_stats = [ ]
	_plug_stats = [ ]

	def on_init( self ):
		self.clean_up( )

	def refresh( self ):
		pass

	def clean_up( self ):
		self._car_stats = [ ]
		self._travel_stats = [ ]
		self._plug_stats = [ ]