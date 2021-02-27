from core.SingletonMetaClass import SingletonMetaClass
import asyncio
import websockets
import os
import threading

class SocketHelper( metaclass = SingletonMetaClass ):

    _ws_clients = [ ]
    _ws_client_message_recipients = [ ]

    _event_loop = None

    def on_init( self ):
        self._event_loop = asyncio.get_event_loop( )

        env_variables = os.environ
        ws_host = env_variables[ 'SIMULATOR_HOST' ]
        ws_port = env_variables[ 'SIMULATOR_WS_PORT' ]      

        print( '``````````Serving WS...``````````' )      
        init_ws_task = websockets.serve( self.on_connect_ws_client, ws_host, ws_port )        
        self._event_loop.run_until_complete( init_ws_task )
        serve_ws_thread = threading.Thread( target = lambda : self._event_loop.run_forever( ) )
        serve_ws_thread.start( )
        print( '``````````Serving WS... done!``````````' )            
        
    async def on_connect_ws_client( self, client, path ):
        try:
            self.register_ws_client( client )            
            await client.send( 'WS -- CONNECTED SUCCESSFULLY!' )
            while True:
                message = await client.recv( )
                self.on_client_message_received( message )           
                asyncio.sleep( 0 )                     
        except:
            self.unregister_ws_client( client )

    def register_ws_client( self, client ):
        self._ws_clients.append( client )

    def unregister_ws_client( self, client ):     
        self._ws_clients.remove( client )                 

    def attach_on_client_message_received( self, recipient ):    
        self._ws_client_message_recipients.append( recipient )  

    def detach_on_client_message_received( self, recipient ):
        self._ws_client_message_recipients.remove( recipient )                        

    def on_client_message_received( self, message ):
        for r in self._ws_client_message_recipients:
            r( message )

    def send_message_to_clients( self, message ):
        asyncio.run_coroutine_threadsafe( self._send_message( message ), self._event_loop )

    async def _send_message( self, message ):
        for c in self._ws_clients:
            try:    
                await c.send( message )
            except:
                self.unregister_ws_client( c )
