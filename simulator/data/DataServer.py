from flask import Blueprint
import asyncio
import websockets
import os

api = Blueprint( "DataServer", __name__ )

class DataServer:

	_simulator = None

	def __init__( self, simulator ):
		#TODO
		self._simulator = simulator

	def get_blueprint( self ):
		return api		

	def run( self ):
		env_variables = os.environ

		ws_host = env_variables[ 'SIMULATOR_HOST' ]
		ws_port = env_variables[ 'SIMULATOR_WS_PORT' ]
		print( '``````````Initializing WS... (at {}:{})``````````'.format( ws_host, ws_port) )
		init_ws = websockets.serve( self.on_connect_ws, ws_host, ws_port )
		event_loop = asyncio.get_event_loop( )
		event_loop.run_until_complete( init_ws )		
		event_loop.run_forever()
		print( '``````````Initializing WS... done!``````````' )	

	async def on_connect_ws( self, websocket, path ):
		name = await websocket.recv( )
		print( f"< {name}" )

		greeting = f"Hello {name}!"

		await websocket.send( greeting )
		print( f"> {greeting}" )		

	@api.route( '/' )
	def root( ):
		return "test root!"
