import requests
import sys
import traceback as tb
import threading
import atexit

from config.ConfigurationHelper import ConfigurationHelper

class WebhookHelper:

	__TIMEOUT = 3

	__COLORS = {
		'SUCCESS': '#00ff00',
		'WARNING': '#ffaa00',
		'ERROR': '#ff0000',
		'INFO': '#cccccc'		
	}

	__MESSAGE_TEMPLATE = '*EnergySim*:\n{}'

	def attach( ):
		WebhookHelper.attach_errors( )
		WebhookHelper.attach_signals( )

	def attach_errors( ):
		sys_excepthook_orig = sys.excepthook

		def on_sys_exception( exctype, value, traceback ):
			traceback_details = ( '* Type: {}\n'.format( exctype ) + 
				'* Value: {}\n'.format( value ) + 
				'* Traceback: {}\n'.format( '\n'.join( tb.extract_tb( traceback ).format( ) ) ) )
			WebhookHelper.send_message( 'Error:\n{}'.format( traceback_details ), 'ERROR' )
			sys_excepthook_orig( exctype, value, traceback )

		sys.excepthook = on_sys_exception	

		threading_run_orig = threading.Thread.run

		def on_thread_run( *args, **kwargs ):
			try:
				threading_run_orig( *args, **kwargs )
			except:
				sys.excepthook( *sys.exc_info( ) )

		threading.Thread.run = on_thread_run					

	def attach_signals( ):
		def on_exit( ):
			WebhookHelper.send_message( 'Core container terminated!', 'ERROR' )

		atexit.register( on_exit )

	def send_message( message_text, message_type = 'INFO' ):
		message_color = WebhookHelper._get_color( message_type )

		config_helper = ConfigurationHelper( )
		webhook_url = config_helper.get_config_by_key( 'webhook_url' )

		webhook_data = {
			"attachments": 
			[
				{
					"color": message_color,
					"blocks": 
					[
						{
							"type": "section",
							"text": 
							{
								"type": "mrkdwn",
								"text": WebhookHelper.__MESSAGE_TEMPLATE.format( message_text )
							}
						}
					]
				}
			]
		}

		try:
			req = requests.post( webhook_url, json = webhook_data, timeout = WebhookHelper.__TIMEOUT )
		except:
            		print( '> WH EXCEPTION!' )
            		tb.print_exc( )
            		print( '< WH EXCEPTION!' )

	def _get_color( message_type = 'INFO' ):
		message_color = WebhookHelper.__COLORS[ message_type ]
		return message_color		