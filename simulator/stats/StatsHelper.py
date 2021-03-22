from base.SingletonMetaClass import SingletonMetaClass
from core.CarStatuses import CarStatuses

class StatsHelper( metaclass = SingletonMetaClass ):

	_last_datetime_str = ''

	_car_stats = { }
	_travel_stats = { }
	_plug_stats = { }

	def on_init( self ):
		self.clean_up( )	

	def update_stats( self, sim_data ):
		cars = sim_data[ 'cars' ]
		plugs = sim_data[ 'plugs' ]		

		car_stats_cols = self._car_stats[ 'columns' ]			
		if len( car_stats_cols ) == 1:
			for c in cars:
				car_stats_cols.append( { 'type': 'number', 'label': 'Car #{}'.format( c[ 'id' ] ) } )

		plug_stats_cols = self._plug_stats[ 'columns' ]
		if len( plug_stats_cols ) == 1:
			for p in plugs:
				plug_stats_cols.append( { 'type': 'number', 'label': 'Plug #{}'.format( p[ 'id' ] ) } )				

		# update, if necessary
		sim_datetime_str = sim_data[ 'sim_datetime' ]
		if ( not self._last_datetime_str ) or ( self._last_datetime_str != sim_datetime_str ):
			
			car_stats_new_row = [ sim_datetime_str ]
			for c in cars:
				car_stats_new_row.append( c[ 'battery_level' ] )
			
			self._car_stats[ 'rows' ].append( car_stats_new_row )

			plug_stats_new_row = [ sim_datetime_str ]
			for p in plugs:
				plug_stats_new_row.append( p[ 'energy_consumption' ] )

			self._plug_stats[ 'rows' ].append( plug_stats_new_row )

			travel_stats_new_row = [ sim_datetime_str ]
			number_of_traveling_cars = len( [ c for c in cars if c[ 'status' ] ==  CarStatuses.STATUS_TRAVELING ] )
			travel_stats_new_row.append( number_of_traveling_cars )

			self._travel_stats[ 'rows' ].append( travel_stats_new_row )

	def get_stats( self ):
		return {
			'home_stats' : {
				'columns' : [ { 'type': 'string', 'label': 'Task' }, { 'type': 'number', 'label': 'Hours per Day' } ],
				'rows' : [ [ 'Work', 11 ], [ 'Eat', 2 ], [ 'Watch TV', 4 ] ]
			},
			'car_stats' : self._car_stats,
			'plug_stats' : self._plug_stats,
			'travel_stats' : self._travel_stats
		}

	def clean_up( self ):
		self._car_stats = {
	                'columns' : [ { 'type': 'date', 'label': 'Date' } ],
	                'rows' : [ ]
            	}
		self._travel_stats = {
			'columns' : [ { 'type': 'date', 'label': 'Date' }, { 'type': 'number', 'label': 'No. of traveling cars' } ],
	                'rows' : [ ]
		}
		self._plug_stats = {
			'columns' : [ { 'type': 'date', 'label': 'Date' } ],
	                'rows' : [ ]
		}