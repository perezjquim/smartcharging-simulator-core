from flask import Blueprint, Response
import json

from base.SingletonMetaClass import *
from data.DataExporter import *		

api = Blueprint( "DataServer", __name__ )

class DataServer( metaclass = SingletonMetaClass ):

	__simulator = None

	def __init__( self, simulator ):
		DataServer.__simulator = simulator

	def get_blueprint( self ):
		return api

	@api.route( '/plugs' )
	def get_plugs( ):
		data_exporter = DataExporter( )
		plugs_sim_data = data_exporter.get_plugs_data( DataServer.__simulator )

		response = Response( json.dumps( plugs_sim_data ), mimetype = 'application/json' )		
		return response

	def _get_plug_by_id( plug_id ):
		data_exporter = DataExporter( )
		plugs_sim_data = data_exporter.get_plugs_data( DataServer.__simulator )
		selected_plug = list( filter( lambda p: p[ 'id' ] == plug_id, plugs_sim_data ) )
		if len( selected_plug ) > 0:
			return selected_plug[ 0 ]

	@api.route( '/plugs/<int:plug_id>' )
	def get_plug_by_id( plug_id ):
		selected_plug = DataServer._get_plug_by_id( plug_id )

		response = None

		if selected_plug:
			response = Response( json.dumps( selected_plug ), mimetype = 'application/json', status = 200 )
		else:
			response = Response( 'NOK', status = 404 )					

		return response

	@api.route( '/plugs/<int:plug_id>/set_status/<string:new_status>' )
	def set_plug_status( plug_id, new_status ):
		selected_plug = DataServer._get_plug_by_id( plug_id )

		response = None

		if selected_plug:
			DataServer.__simulator.set_charging_plug_status( plug_id, new_status )
			response = Response( 'OK', status = 200 )
		else:
			response = Response( 'NOK', status = 404 )					
			
		return response