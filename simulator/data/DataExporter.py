from pony.orm import *

from base.SingletonMetaClass import *
from stats.StatsHelper import *		

class DataExporter( metaclass = SingletonMetaClass ):

	_stats_helper = None

	def on_init( self ):
		self._stats_helper = StatsHelper( )
		self._stats_helper.on_init( )

	def get_plugs_data( self, simulator ):

		plugs_sim_data = [ ]				

		plugs = simulator.get_charging_plugs( )

		for p in plugs:
			p.lock( )

			plug_data = p.get_data( )
			plugs_sim_data.append( plug_data )

			p.unlock( )

		plugs_sim_data.sort( key = lambda x : x[ 'id' ] )

		return plugs_sim_data

	def get_cars_data( self, simulator ):

		cars_sim_data = [ ]

		cars = simulator.get_cars( )

		for c in cars:
			c.lock( )
			
			car_data = c.get_data( )
			cars_sim_data.append( car_data )

			c.unlock( )

		cars_sim_data.sort( key = lambda x : x[ 'id' ] )

		return cars_sim_data			
	
	def get_travel_data( self, simulator ):

		travels_sim_data = [ ]

		cars = simulator.get_cars( )

		for c in cars:
			c.lock( )
			
			car_data = c.get_data( )

			travel_data = car_data[ 'travels' ]
			travels_sim_data += travel_data	

			c.unlock( )

		travels_sim_data.sort( key = lambda x : x[ 'id' ] )			

		return travels_sim_data

	def get_charging_period_data( self, simulator ):

		charging_periods_sim_data = [ ]

		cars = simulator.get_cars( )

		for c in cars:
			c.lock( )
			
			car_data = c.get_data( )

			charging_period_data = car_data[ 'charging_periods' ]
			charging_periods_sim_data += charging_period_data		

			c.unlock( )	
			
		charging_periods_sim_data.sort( key = lambda x : x[ 'id' ] )	
		
		return charging_periods_sim_data				

	def prepare_simulation_data( self, simulator ):	
		cars_sim_data = self.get_cars_data( simulator )
		travels_sim_data = self.get_travel_data( simulator )
		charging_periods_sim_data = self.get_charging_period_data( simulator )
		plugs_sim_data = self.get_plugs_data( simulator )	

		sim_datetime = simulator.get_current_datetime( )
		sim_datetime_str = '' 
		if sim_datetime:
			sim_datetime_str = sim_datetime.isoformat( )

		data_to_export = {
			'sim_datetime': sim_datetime_str,
			'cars': cars_sim_data, 
			'travels': travels_sim_data, 
			'charging_periods': charging_periods_sim_data,
			'plugs': plugs_sim_data
		}

		self._stats_helper.update_stats( data_to_export )
		stats = self._stats_helper.get_stats( )

		data_to_export.update( stats )

		return data_to_export