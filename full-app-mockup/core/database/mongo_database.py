from .database import Database
from pymongo import MongoClient

class MongoDatabase(Database):
    def __init__(self, database_info):
        super().__init__(database_info)
        self.client = MongoClient(self.database_info['host'], self.database_info['port'])
        self.db = self.client[self.database_info['database_name']]