from core.SingletonMetaClass import SingletonMetaClass
import asyncio
import websockets
import os
import threading
import json
import traceback

class SocketHelper( metaclass = SingletonMetaClass ):

    _ws_clients = [ ]
    _ws_client_connection_listeners = [ ]
    _ws_client_message_listeners = [ ]

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
            init_message_str = self._stringify_message( 'log', 'WS -- CONNECTED SUCCESSFULLY!' )
            await client.send( init_message_str )
            self.on_client_connected( client )
            while True:
                message = await self._receive_message( client )
                self.on_client_message_received( message )           
                asyncio.sleep( 0 )                     
        except Exception as exc:
            print( 'EXCEPTION: {}'.format( exc ) )
            traceback.print_exc( )            
            self.unregister_ws_client( client )

    async def _receive_message( self, client ):
        message_str = await client.recv( )
        message = json.loads( message_str )
        return message

    def register_ws_client( self, client ):
        self._ws_clients.append( client )

    def unregister_ws_client( self, client ):     
        self._ws_clients.remove( client )             

    def attach_on_client_connected( self, listener ):    
        self._ws_client_connection_listeners.append( listener )              

    def detach_on_client_connected( self, listener ):    
        self._ws_client_connection_listeners.remove( listener )             

    def attach_on_client_message_received( self, listener ):    
        self._ws_client_message_listeners.append( listener )  

    def detach_on_client_message_received( self, listener ):
        self._ws_client_message_listeners.remove( listener )      

    def on_client_connected( self, client ):
        for l in self._ws_client_connection_listeners:
            l( client )

    def on_client_message_received( self, message ):
        for l in self._ws_client_message_listeners:
            l( message )

    def send_message_to_clients( self, message_type, message_value, client=None ):
        asyncio.run_coroutine_threadsafe( self._send_message( message_type, message_value, client ), self._event_loop )    

    def _stringify_message( self, message_type, message_value ):
        message = { 'message_type' : message_type, 'message_value' : message_value }
        message_str = json.dumps( message )
        return message_str

    async def _send_message( self, message_type, message_value, client=None ):
        message_str = self._stringify_message( message_type, message_value )

        if client:

            try:
                await client.send( message_str )
            except Exception as exc:
                print( 'EXCEPTION: {}'.format( exc ) )
                traceback.print_exc( )                            
                self.unregister_ws_client( client )

        else:                
            
            for c in self._ws_clients:
                try:    
                    await c.send( message_str )
                except Exception as exc:
                    print( 'EXCEPTION: {}'.format( exc ) )
                    traceback.print_exc( )                            
                    self.unregister_ws_client( c )
