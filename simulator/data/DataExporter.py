from base.SingletonMetaClass import SingletonMetaClass
from stats.StatsHelper import StatsHelper

class DataExporter( metaclass = SingletonMetaClass ):

	_stats_helper = None

	def on_init( self ):
		self._stats_helper = StatsHelper( )
		self._stats_helper.on_init( )
		pass

	def prepare_simulation_data( self, simulator ):	
		cars_sim_data = [ ]
		travels_sim_data = [ ]
		charging_periods_sim_data = [ ]

		cars = simulator.get_cars( )

		for c in cars:
			c.lock( )
			
			car_data = c.get_data( )
			cars_sim_data.append( car_data )

			travel_data = car_data[ 'travels' ]
			travels_sim_data += travel_data

			charging_period_data = car_data[ 'charging_periods' ]
			charging_periods_sim_data += charging_period_data		

			c.unlock( )

		plugs_sim_data = [ ]		

		plugs = simulator.get_charging_plugs( )

		for p in plugs:
			p.lock( )

			plug_data = p.get_data( )
			plugs_sim_data.append( plug_data )

			p.unlock( )

		cars_sim_data.sort( key = lambda x : x[ 'id' ] )
		travels_sim_data.sort( key = lambda x : x[ 'id' ] )
		charging_periods_sim_data.sort( key = lambda x : x[ 'id' ] )	
		plugs_sim_data.sort( key = lambda x : x[ 'id' ] )			

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