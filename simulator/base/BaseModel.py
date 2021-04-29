from sqlobject import *

class BaseModel( SQLObject ):
	
	def get_id( self ):
		return self._id