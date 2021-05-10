from sqlobject import *
from sqlobject.util import csvexport
import os
import importlib

from base.SingletonMetaClass import SingletonMetaClass

class DBHelper( metaclass = SingletonMetaClass ):

	__PROVIDER = 'sqlite'
	__FILE_PATH = 'vol/energysim.db'
	__OPTIONS = '?timeout=15'

	__MODELS_INFO = [
		{
			"class_path": "model.SimulationModel",
			"class_name": "SimulationModel"
		},
		{
			"class_path": "model.objects.CarModel",
			"class_name": "CarModel"
		},
		{
			"class_path": "model.objects.PlugModel",
			"class_name": "PlugModel"
		},
		{
			"class_path": "model.objects.LogModel",
			"class_name": "LogModel"
		},
		{
			"class_path": "model.objects.StatModel",
			"class_name": "StatModel"
		},
		{
			"class_path": "model.events.TravelModel",
			"class_name": "TravelModel"
		},
		{
			"class_path": "model.events.ChargingPeriodModel",
			"class_name": "ChargingPeriodModel"
		}															
	]

	_model_classes = [ ]

	def __init__( self ):
		db_filename = os.path.abspath( DBHelper.__FILE_PATH )	
		connection_string = '{}:{}{}'.format( DBHelper.__PROVIDER, db_filename, DBHelper.__OPTIONS )
		connection = connectionForURI( connection_string )
		self._prepare( connection )
		sqlhub.processConnection = connection

		self._model_classes = [ ]

		for m in DBHelper.__MODELS_INFO:
			class_path = m[ 'class_path' ]
			class_name = m[ 'class_name' ]
			model_class = getattr( importlib.import_module( class_path ), class_name )
			self._model_classes.append( model_class )

	def on_init( self ):
		self._prepare_tables( )

	def _prepare( self, connection ):
		connection.queryAll( 'pragma journal_mode = wal;' )
		connection.queryAll( 'pragma synchronous = normal;' )
		connection.queryAll( 'pragma temp_store = memory;' )

	def _prepare_tables( self ):				
		for m in self._model_classes:
			m.createTable( ifNotExists = True)

	def export_data( self ):
		exported_data = csvexport.export_csv_zip( self._model_classes )
		return exported_data