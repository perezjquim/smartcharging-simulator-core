from core.Simulator import Simulator
from data.DataServer import DataServer
from flask import Flask

simulator = Simulator( )
simulator.on_init( )

data_server = DataServer( simulator )

app = Flask( __name__ )
app.register_blueprint( data_server.get_blueprint( ) )