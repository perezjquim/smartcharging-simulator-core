import inspect

class DebugHelper:

	def get_caller( ):
		stack = inspect.stack( )[ 2 ]
		class_name = stack[ 1 ]
		method_name = stack[ 3 ]
		return '{}::{}'.format( class_name, method_name )