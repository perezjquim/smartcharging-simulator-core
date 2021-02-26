from flask import Blueprint
import asyncio
import websockets
import os

api = Blueprint( "DataServer", __name__ )

class DataServer:

	_simulator = None

	def __init__( self, simulator ):
		self._simulator = simulator

	def get_blueprint( self ):
		return api		

	@api.route( '/' )
	def root( ):
		return "test root!"