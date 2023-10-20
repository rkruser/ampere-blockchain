from .user_mongo_database import UserMongoDatabase

def CreateDatabaseInterface(database_type, database_info):
    if database_type == 'mongodb':
        return UserMongoDatabase(database_info)
    else:
        raise Exception('Invalid database type')