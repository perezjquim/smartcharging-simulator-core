from flask import Blueprint, Response
import json
from datetime import datetime 

from base.SingletonMetaClass import SingletonMetaClass

api = Blueprint( "DataServer", __name__ )

class DataServer( metaclass = SingletonMetaClass ):

	__simulator = None

	def __init__( self, simulator ):
		DataServer.__simulator = simulator

	def get_blueprint( self ):
		return api

	@api.route( '/plugs' )
	def get_plugs( ):
		simulator = DataServer.__simulator
		current_simulation = simulator.get_current_simulation( )

		response = None

		if current_simulation:

			plugs_sim_data = current_simulation.get_plugs_data( )
			response = Response( json.dumps( plugs_sim_data ), mimetype = 'application/json', status = 200 )		

		else:
			response = Response( 'No simulation available!', status = 404 )				
		
		return response

	def _get_plug_by_id( plug_id ):		
		simulator = DataServer.__simulator
		current_simulation = simulator.get_current_simulation( )

		if current_simulation:

			plugs_sim_data = current_simulation.get_plugs_data( )

			selected_plug = [ p for p in plugs_sim_data if p[ 'id' ] == plug_id ]
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
			simulator = DataServer.__simulator
			current_simulation = simulator.get_current_simulation( )			
			current_simulation.set_charging_plug_status( plug_id, new_status )
			response = Response( 'OK', status = 200 )
		else:
			response = Response( 'NOK', status = 404 )					
			
		return response

	@api.route( '/export' )
	def export_data( ):
		simulator = DataServer.__simulator
		exported_data = simulator.export_data( )

		response = None

		if exported_data:

			current_datetime = datetime.now( )
			current_datetime_str = current_datetime.isoformat( )
			zip_filename = 'ENERGYSIM - DATA - {}.zip'.format( current_datetime_str )

			content_disposition = "attachment; filename={};".format( zip_filename )
			response_headers = { "Content-Disposition" : content_disposition }			

			response = Response( exported_data, mimetype = 'application/octet-stream', status = 200, headers = response_headers )	

		else:

			response = Response( 'NOK', status = 500 )

		return response

	@api.route( '/is_simulation_running' )
	def is_simulation_running( ):
		simulator = DataServer.__simulator

		current_simulation = simulator.get_current_simulation( )

		response = None

		if current_simulation:

			is_simulation_running = current_simulation.is_simulation_running( )

			response = Response( json.dumps( { "is_simulation_running": is_simulation_running } ), mimetype = 'application/json', status = 200 )

		else:

			response = Response( json.dumps( { "is_simulation_running" : False } ), mimetype = 'application/json', status = 200 )
			
		return response

	@api.route( '/start_new_sim' )
	def start_new_sim( ):
		simulator = DataServer.__simulator

		current_simulation = simulator.get_current_simulation( )

		response = None

		if current_simulation:

			is_simulation_running = current_simulation.is_simulation_running( )

			if is_simulation_running:

				response = Response( 'NOK', status = 500 )

			else:

				simulator.on_start( )
				response = Response( 'OK', status = 200 )

		else:

			response = Response( 'NOK', status = 500 )
			
		return response