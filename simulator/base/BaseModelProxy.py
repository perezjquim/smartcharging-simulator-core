import importlib

class BaseModelProxy( ):

	_is_read_only = False
	_model = None

	def __init__( self, model_class_path = '', model_class_name = '', model_instance = None ):
		super( ).__init__( )

		self.set_read_only( model_instance != None )

		if not model_instance:
			model_class = getattr( importlib.import_module( model_class_path ), model_class_name )
			model_instance = model_class( )

		self.set_model( model_instance )	

	def get_model( self ):
		return self._model

	def set_model( self, model ):
		self._model = model

	def is_read_only( self ):
		return self._is_read_only

	def set_read_only( self, is_read_only ):
		self._is_read_only = is_read_only

	def get_id( self ):
		return self._model.get_id( )

	def get_data( self ):
		return {
			'id' : self.get_id( )
		}