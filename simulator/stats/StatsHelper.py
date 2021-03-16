from base.SingletonMetaClass import SingletonMetaClass

class StatsHelper( metaclass = SingletonMetaClass ):

	_car_stats = [ ]
	_travel_stats = [ ]
	_plug_stats = [ ]

	def on_init( self ):
		self.clean_up( )

	def update_stats( self, sim_data ):
		pass

	def get_stats( self ):
		return {
			'home_stats' : {
				'columns' : [ { 'type': 'string', 'label': 'Task' }, { 'type': 'number', 'label': 'Hours per Day' } ],
				'rows' : [ [ 'Work', 11 ], [ 'Eat', 2 ], [ 'Watch TV', 4 ] ]
			}
		}

	def clean_up( self ):
		self._car_stats = [ ]
		self._travel_stats = [ ]
		self._plug_stats = [ ]