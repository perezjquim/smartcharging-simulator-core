from flask import Flask

from base.ImportHelper import ImportHelper

Simulator = ImportHelper.import_class( 'core.Simulator' )
SocketHelper = ImportHelper.import_class( 'data.SocketHelper' )
DataServer = ImportHelper.import_class( 'data.DataServer' )

simulator = Simulator( )
simulator.on_init( )

data_server = DataServer( simulator )

app = Flask( __name__ )
app.register_blueprint( data_server.get_blueprint( ) )