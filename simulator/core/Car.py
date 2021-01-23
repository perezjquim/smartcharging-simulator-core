from . import *

class Car:

	def __init__( self ):
		self._batteryLevel = 0
		#TODO

	def getBatteryLevel( self ):
		return self._batteryLevel

	def setBatteryLevel( self, batteryLevel ):
		self._batteryLevel = batteryLevel
