import asyncio
import websockets
import os
import threading
import json
import sys

from base.SingletonMetaClass import SingletonMetaClass
    
class SocketHelper( metaclass = SingletonMetaClass ):

    __SLEEP = 1
    __TIMEOUT = 5

    _ws_clients = [ ]
    _ws_client_connection_listeners = [ ]
    _ws_client_message_listeners = [ ]

    _event_loop = None

    def on_init( self ):
        self._event_loop = asyncio.get_event_loop( )
        self._messages_to_be_sent_queue = asyncio.Queue( )

        env_variables = os.environ
        ws_host = env_variables[ 'SIMULATOR_HOST' ]
        ws_port = env_variables[ 'SIMULATOR_WS_PORT' ]      

        self.serve( )

    def serve( self ):
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
            await asyncio.wait_for( client.send( init_message_str ), timeout = SocketHelper.__TIMEOUT )
            self.on_client_connected( client )
            while True:
                message = await self._receive_message( client )
                self.on_client_message_received( message )           
                asyncio.sleep( SocketHelper.__SLEEP )  
        except websockets.exceptions.ConnectionClosedOK:
            self.unregister_ws_client( client )
        except:
            print( '> SOCKET - RECV ERROR!' )            
            self.unregister_ws_client( client )            
            sys.excepthook( *sys.exc_info( ) )
            print( '< SOCKET - RECV ERROR!' )            

    async def _receive_message( self, client ):
        message_str = await client.recv( )
        message = json.loads( message_str )
        return message

    def register_ws_client( self, client ):
        if client not in self._ws_clients:
            self._ws_clients.append( client )

    def unregister_ws_client( self, client ):
        if client in self._ws_clients:     
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
                    await asyncio.wait_for( client.send( message_str ), timeout = SocketHelper.__TIMEOUT ) 
                except websockets.exceptions.ConnectionClosedOK:
                    self.unregister_ws_client( client )
                except:
                    print( '> SOCKET - SEND ERROR!' )
                    self.unregister_ws_client( client )                
                    sys.excepthook( *sys.exc_info( ) )      
                    print( '< SOCKET - SEND ERROR!' )                  

            else:                
                
                for c in self._ws_clients:
                    try:
                        await asyncio.wait_for( c.send( message_str ), timeout = SocketHelper.__TIMEOUT )
                    except websockets.exceptions.ConnectionClosedOK:
                        self.unregister_ws_client( client )
                    except:
                        print( '> SOCKET - SEND ERROR!' )
                        self.unregister_ws_client( client )                
                        sys.excepthook( *sys.exc_info( ) )      
                        print( '< SOCKET - SEND ERROR!' )             
                 
        asyncio.sleep( SocketHelper.__SLEEP )