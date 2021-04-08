from peewee import Model

from .DBHelper import *

class BaseModel( Model ):

	class Meta:
		database = None