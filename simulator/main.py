from flask import Flask

from model.DBHelper import DBHelper
from core.Simulator import Simulator
from data.DataServer import DataServer

db_helper = DBHelper( )
db_helper.on_init( )

simulator = Simulator( )
simulator.on_init( )

data_server = DataServer( simulator )

app = Flask( __name__ )
app.register_blueprint( data_server.get_blueprint( ) )