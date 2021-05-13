from flask import Flask
from flask_cors import CORS

from data.WebhookHelper import WebhookHelper
from model.DBHelper import DBHelper
from core.Simulator import Simulator
from data.DataServer import DataServer

WebhookHelper.attach( )
WebhookHelper.send_message( 'Core container turned on!', 'SUCCESS' )

db_helper = DBHelper( )
db_helper.on_init( )

simulator = Simulator( )
simulator.on_init( )

data_server = DataServer( simulator )

app = Flask( __name__ )
CORS( app )
app.register_blueprint( data_server.get_blueprint( ) )