import datetime
import random
import string
from .user_database_interface import UserDatabaseInterface
from .mongo_database import MongoDatabase
from ..security import generate_session_key

class UserMongoDatabase(UserDatabaseInterface, MongoDatabase):
    # database_info should be host, port, database_name
    def __init__(self, database_info):
        MongoDatabase.__init__(self, database_info)
        self.users = self.db['users']
        self.sessions = self.db['sessions']

    def login_user(self, username, password):
        user = self.users.find_one({"username": username, "password": password})  # Consider hashing the password for better security
        if not user:
            return False  # or raise an appropriate error

        session_id = generate_session_key()
        expiration_time = datetime.datetime.now() + datetime.timedelta(hours=24)
        
        with self.client.start_session() as session:
            with session.start_transaction():
                self.sessions.insert_one({
                    "session_id": session_id,
                    "username": username,
                    "expiration_time": expiration_time
                }, session=session)

                self.users.update_one(
                    {"username": username},
                    {"$push": {"active_sessions": session_id}},
                    session=session
                )

        return True, session_id

    def logout_user(self, username, session_id):
        with self.client.start_session() as session:
            with session.start_transaction():
                self.sessions.delete_one({"session_id": session_id}, session=session)
                self.users.update_one(
                    {"username": username},
                    {"$pull": {"active_sessions": session_id}},
                    session=session
                )

    def verify_user_session(self, session_username, session_id):
        session = self.sessions.find_one({"session_id": session_id, "username": session_username})
        if not session:
            return False
        return datetime.datetime.now() < session['expiration_time']

    def add_user(self, username, password, email, phone_number, permission_level):
        # Consider hashing the password for better security
        self.users.insert_one({
            "username": username,
            "password": password,
            "email": email,
            "phone_number": phone_number,
            "permission_level": permission_level,
            "active_sessions": []
        })

    def has_admin_permissions(self, username):
        user = self.users.find_one({"username": username})
        if not user:
            return False  # or raise an appropriate error
        return user['permission_level'] == 'admin'
