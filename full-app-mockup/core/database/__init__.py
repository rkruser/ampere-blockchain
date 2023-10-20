from .mongo_database import MongoDatabase

def CreateDatabaseInterface(database_type, database_info):
    if database_type == 'mongodb':
        return MongoDatabase(database_info)
    else:
        raise Exception('Invalid database type')