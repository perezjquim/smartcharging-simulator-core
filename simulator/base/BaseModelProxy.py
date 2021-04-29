import importlib

class BaseModelProxy( ):

	_model = None

	def __init__( self, model_path, model_class_name ):
		super( ).__init__( )

		model_class = getattr( importlib.import_module( model_path ), class_name )
		model_instance = model_class( )
		self.set_model( model_instance )

	def get_model( self ):
		return self._model

	def set_model( self, model ):
		self._model = model

	def get_id( self ):
		return self._model.get_id( )