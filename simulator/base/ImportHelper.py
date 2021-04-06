class ImportHelper:

	def import_class( class_path ):
		class_data = class_path.split( "." )		
		class_name = class_data[ -1 ]		

		module = __import__( class_path, fromlist = [ class_name ] )
		
		return getattr( module, class_name )