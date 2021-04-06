from peewee import Model

from base.ImportHelper import ImportHelper

DBHelper = ImportHelper.import_class( 'model.DBHelper' )

db_helper = DBHelper( )
db = db_helper.get_db( )

class BaseModel( Model ):
    class Meta:
        database = db
