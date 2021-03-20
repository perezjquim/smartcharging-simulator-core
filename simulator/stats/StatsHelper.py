from base.SingletonMetaClass import SingletonMetaClass

class StatsHelper( metaclass = SingletonMetaClass ):

	_last_datetime_str = ''

	_car_stats = { }
	_travel_stats = { }
	_plug_stats = { }

	def on_init( self ):
		self.clean_up( )

	def update_stats( self, sim_data ):		
		if len( self._car_stats[ 'columns' ] ) < 1:
			self._car_stats[ 'columns' ] = [ { 'type': 'date', 'label': 'Date' } ]
			number_of_cars = len( sim_data[ 'cars' ] )
			for n in range( number_of_cars ):
				self._car_stats[ 'columns' ].append( { 'type': 'number', 'label': 'Car #{}'.format( n ) } )

			#TODO

		# update, if necessary
		sim_datetime_str = sim_data[ 'sim_datetime' ]
		if ( not self._last_datetime_str ) or ( self._last_datetime_str != sim_datetime_str ):
			
			car_stats_new_row = [ sim_datetime_str ]
			for c in sim_data[ 'cars' ]:
				car_stats_new_row.append( c[ 'battery_level' ] )
			
			self._car_stats[ 'rows' ].append( car_stats_new_row )

	def get_stats( self ):
		return {
			'home_stats' : {
				'columns' : [ { 'type': 'string', 'label': 'Task' }, { 'type': 'number', 'label': 'Hours per Day' } ],
				'rows' : [ [ 'Work', 11 ], [ 'Eat', 2 ], [ 'Watch TV', 4 ] ]
			},
			'car_stats' : self._car_stats
		}

	def clean_up( self ):
		self._car_stats = {
	                'columns' : [ ],
	                'rows' : [ ]
            	}
		self._travel_stats = [ ]
		self._plug_stats = [ ]