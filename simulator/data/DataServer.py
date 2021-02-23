from flask import Blueprint
import asyncio
import websockets

api = Blueprint( "DataServer", __name__ )

class DataServer:

	_simulator = None

	WS_HOST = '0.0.0.0'
	WS_PORT = 9002

	def __init__( self, simulator ):
		#TODO
		self._simulator = simulator

	def get_blueprint( self ):
		return api		

	def run( self ):
		#TODO
		api.run( )

		init_ws = websockets.serve( self.on_connect_ws, DataServer.WS_HOST, DataServer.WS_PORT )

		event_loop = asyncio.get_event_loop( )
		event_loop.run_until_complete( init_ws )		
		event_loop.run_forever()		

	async def on_connect_ws(websocket, path):
		name = await websocket.recv()
		print(f"< {name}")

		greeting = f"Hello {name}!"

		await websocket.send(greeting)
		print(f"> {greeting}")		

	@api.route( '/' )
	def root( ):
		return "test root!"
