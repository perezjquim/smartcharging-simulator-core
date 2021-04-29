from sqlobject import *

from .CarEventModel import *

class ChargingPeriodModel( CarEventModel ):

	class sqlmeta:
		table = 'ChargingPeriods'	

	_plug = ForeignKey( 'PlugModel', default = None, dbName = 'plug_id' )

	def get_plug( self ):
		return self._plug	

	def set_plug( self, new_plug ):
		self._plug = new_plug