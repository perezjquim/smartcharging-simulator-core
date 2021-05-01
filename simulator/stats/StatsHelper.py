import random

from core.constants.CarConstants import *

from core.objects.Stat import *

class StatsHelper( ):

	_simulation = None

	_last_datetime_str = ''

	_car_stats = None
	_travel_stats = None
	_plug_stats = None

	def __init__( self, simulation ):
		self._simulation = simulation

		self._last_datetime_str = ''

		self._car_stats = Stat( simulation, 'car-stats' )
		self._car_stats.set_data({
	                'labels' : [ ],
	                'datasets' : [ ]
            	})

		self._travel_stats = Stat( simulation, 'travel-stats' )
		self._travel_stats.set_data({
	                'labels' : [ ],
	                'datasets' : [ ]
            	})

		self._plug_stats = Stat( simulation, 'plug-stats' )
		self._plug_stats.set_data({
	                'labels' : [ ],
	                'datasets' : [ ]
            	})

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

				car_stats = self._car_stats.get_data( )
				car_stats_datasets = car_stats[ 'datasets' ]
				car_stats_data = car_stats_datasets[ i ][ 'data' ]
				car_stats_data.append( car_battery_level )
				self._car_stats.set_data( car_stats )
			
			for i in range( len( plugs ) ):
				plug = plugs[ i ]
				plug_energy_consumption = plug[ 'energy_consumption' ]

				plug_stats = self._plug_stats.get_data( )
				plug_stats_datasets = plug_stats[ 'datasets' ]
				plug_stats_data = plug_stats_datasets[ i ][ 'data' ]
				plug_stats_data.append( plug_energy_consumption )	
				self._plug_stats.set_data( plug_stats )

			number_of_traveling_cars = len( [ c for c in cars if c[ 'status' ] ==  CarConstants.STATUS_TRAVELING ] )
			travel_stats = self._travel_stats.get_data( )
			travel_stats_datasets = travel_stats[ 'datasets' ]
			travel_stats_data = travel_stats_datasets[ 0 ][ 'data' ]
			travel_stats_data.append( number_of_traveling_cars )	
			self._travel_stats.set_data( travel_stats )

	def get_data( self ):
		return {
			'car_stats' : self._car_stats.get_data( ),
			'plug_stats' : self._plug_stats.get_data( ),
			'travel_stats' : self._travel_stats.get_data( )
		}
		
	def _prepare_datasets( self, cars, plugs ):
		car_stats = self._car_stats.get_data( )
		car_stats_datasets = car_stats[ 'datasets' ]
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

			self._car_stats.set_data( car_stats )

		plug_stats = self._plug_stats.get_data( )
		plug_stats_datasets = plug_stats[ 'datasets' ]
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

			self._plug_stats.set_data( plug_stats )				

		travel_stats = self._travel_stats.get_data( )
		travel_stats_datasets = travel_stats[ 'datasets' ]
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

			self._travel_stats.set_data( travel_stats )				

	def _update_labels( self, sim_datetime_str ):
		car_stats = self._car_stats.get_data( )
		car_stats_labels = car_stats[ 'labels' ]			
		car_stats_labels.append( sim_datetime_str )
		self._car_stats.set_data( car_stats )

		plug_stats = self._plug_stats.get_data( )
		plug_stats_labels = plug_stats[ 'labels' ]
		plug_stats_labels.append( sim_datetime_str )
		self._plug_stats.set_data( plug_stats )

		travel_stats = self._travel_stats.get_data( )
		travel_stats_labels = travel_stats[ 'labels' ]			
		travel_stats_labels.append( sim_datetime_str )	
		self._travel_stats.set_data( travel_stats )

	def _generate_color( self ):
		color_hex = hex( random.randint( 0, 0xFFFFFF ) )[ 2: ]
		color_str = '#{}'.format( color_hex )
		return color_str