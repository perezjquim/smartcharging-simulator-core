import random

from base.SingletonMetaClass import *
from core.CarStatuses import *		

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

		sim_datetime_str = sim_data[ 'sim_datetime' ]		

		self._prepare_datasets( cars, plugs )

		# update data, if necessary
		if ( not self._last_datetime_str ) or ( self._last_datetime_str != sim_datetime_str ):
								
			self._update_labels( sim_datetime_str )
			
			for i in range( len( cars ) ):
				car = cars[ i ]
				car_battery_level = car[ 'battery_level' ]

				car_stats_datasets = self._car_stats[ 'datasets' ]
				car_stats_data = car_stats_datasets[ i ][ 'data' ]
				car_stats_data.append( car_battery_level )
			
			for i in range( len( plugs ) ):
				plug = plugs[ i ]
				plug_energy_consumption = plug[ 'energy_consumption' ]

				plug_stats_datasets = self._plug_stats[ 'datasets' ]
				plug_stats_data = plug_stats_datasets[ i ][ 'data' ]
				plug_stats_data.append( plug_energy_consumption )	

			number_of_traveling_cars = len( [ c for c in cars if c[ 'status' ] ==  CarStatuses.STATUS_TRAVELING ] )
			travel_stats_datasets = self._travel_stats[ 'datasets' ]
			travel_stats_data = travel_stats_datasets[ 0 ][ 'data' ]
			travel_stats_data.append( number_of_traveling_cars )	

	def get_stats( self ):
		return {
			'car_stats' : self._car_stats,
			'plug_stats' : self._plug_stats,
			'travel_stats' : self._travel_stats
		}

	def clean_up( self ):
		self._car_stats = {
	                'labels' : [ ],
	                'datasets' : [ ]
            	}
		self._travel_stats = {
	                'labels' : [ ],
	                'datasets' : [ ]
		}
		self._plug_stats = {
	                'labels' : [ ],
	                'datasets' : [ ]
		}

	def _prepare_datasets( self, cars, plugs ):
		car_stats_datasets = self._car_stats[ 'datasets' ]
		if len( car_stats_datasets ) == 0:

			for c in cars:
				label = 'Car #{}'.format( c[ 'id' ] )
				color = self._generate_color( )
				car_stats_datasets.append( {
					'label': label,
					'backgroundColor': color,
					'borderColor': color,
					'fill': False,
					'data': [ ]
				} )

		plug_stats_datasets = self._plug_stats[ 'datasets' ]
		if len( plug_stats_datasets ) == 0:

			for p in plugs:
				label = 'Plug #{}'.format( p[ 'id' ] )
				color = self._generate_color( )
				plug_stats_datasets.append( {
					'label': label,
					'backgroundColor': color,
					'borderColor': color,
					'fill': False,
					'data': [ ]
				} )	

		travel_stats_datasets = self._travel_stats[ 'datasets' ]
		if len( travel_stats_datasets ) == 0:

			label = 'No. of traveling cars'
			color = self._generate_color( )
			travel_stats_datasets.append( {
				'label': label,
				'backgroundColor': color,
				'borderColor': color,
				'fill': False,
				'data': [ ]
			} )					

	def _update_labels( self, sim_datetime_str ):
		car_stats_labels = self._car_stats[ 'labels' ]			
		car_stats_labels.append( sim_datetime_str )

		plug_stats_labels = self._plug_stats[ 'labels' ]
		plug_stats_labels.append( sim_datetime_str )

		travel_stats_labels = self._travel_stats[ 'labels' ]			
		travel_stats_labels.append( sim_datetime_str )	

	def _generate_color( self ):
		color_hex = hex( random.randint( 0, 0xFFFFFF ) )[ 2: ]
		color_str = '#{}'.format( color_hex )
		return color_str