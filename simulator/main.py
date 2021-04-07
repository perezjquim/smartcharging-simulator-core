from base.ImportHelper import ImportHelper
from flask import Flask

import core.Simulator
import data.DataServer

simulator = Simulator( )
simulator.on_init( )

data_server = DataServer( simulator )

app = Flask( __name__ )
app.register_blueprint( data_server.get_blueprint( ) )