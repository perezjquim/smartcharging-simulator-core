import threading
import time
from datetime import date, datetime, timedelta

from base.BaseModelProxy import *

from core.objects.Car import *

class CarEvent( BaseModelProxy ):

	_car = None

	_thread = None

	def __init__( self, model_class_path, model_class_name, car ):
		super( ).__init__( model_class_path, model_class_name )

		self.set_car( car )

		self._thread = threading.Thread( target = self.run )
		self._thread.start( )	

	def run( self ):
		raise NotImplementedError		

	def get_car( self ):
		return self._car

	def set_car( self, car ):
		self._car = car
		model = self.get_model( )
		model.set_car( car )

	def get_start_datetime( self ):
		model = self.get_model( )		
		return model.get_start_datetime( )

	def get_end_datetime( self ):
		model = self.get_model( )		
		return model.get_end_datetime( )

	def set_start_datetime( self, start_datetime ):
		model = self.get_model( )
		model.set_start_datetime( start_datetime )

	def set_end_datetime( self, end_datetime ):
		model = self.get_model( )
		model.set_end_datetime( end_datetime )		

	def destroy( self ):
		if self._thread:
			self._thread.join( )

	def _is_date_valid( self, date ):
		return date is not datetime( 1, 1, 1 )

	def get_data( self ):
		data = super( ).get_data( )

		car = self.get_car( )
		car_id = car.get_id( )

		start_datetime_str = ''
		end_datetime_str = ''
		
		start_datetime = self.get_start_datetime( )
		if self._is_date_valid( start_datetime ):
			start_datetime_str = start_datetime.isoformat( )

		end_datetime = self.get_end_datetime( )
		if self._is_date_valid( end_datetime ):
			end_datetime_str = end_datetime.isoformat( )

		data.update({
			'car_id' : car_id,
			'start_datetime' : start_datetime_str,
			'end_datetime' : end_datetime_str
		})

		return data
