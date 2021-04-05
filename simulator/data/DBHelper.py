from base.SingletonMetaClass import SingletonMetaClass
import sqlite3 as sql

class DBHelper( metaclass = SingletonMetaClass ):

	__FILE_PATH = 'db/energysim.db'

	_db = None

	def __init__( self ):
		self._db = sql.connect( DBHelper.__FILE_PATH )

	def on_init( self ):
		with self._db:
		    self._db.execute("""
		        CREATE TABLE USER (
		            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		            name TEXT,
		            age INTEGER
		        );
		    """)