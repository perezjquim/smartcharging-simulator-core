import requests

from config.ConfigurationHelper import ConfigurationHelper

class WebhookHelper:
	
	def send_message( message ):
		config_helper = ConfigurationHelper( )
		webhook_url = config_helper.get_config_by_key( 'webhook_url' )
		webhook_data = { 'text': message }
		webhook_headers = { 'Content-type': 'application/json' }
		req = requests.post( webhook_url, webhook_data, headers = webhook_headers )