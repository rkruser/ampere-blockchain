class UserDatabaseInterface:
    # implement
    def login_user(self, username, password):
        raise NotImplementedError()

    # implement
    def logout_user(self, username, session_id):
        raise NotImplementedError()

    # implement
    def verify_user_session(self, session_username, session_id):
        raise NotImplementedError()

    # implement
    def verify_authentication_token(self, token):
        raise NotImplementedError()
    
    # implement
    def add_user(self, username, password, email, phone_number, permission_level):
        raise NotImplementedError()

    # implement
    def has_admin_permissions(self, username):
        raise NotImplementedError()

    def get_user_email(self, username):
        raise NotImplementedError()

    def get_user_phone_number(self, username):
        raise NotImplementedError()

    ## functions from flask-https-server mockup
    def add_invitation(self, invitation_code):
        raise NotImplementedError()

    def verify_invitation(self, invitation_code):
        raise NotImplementedError()


    def remove_user(self, username):
        raise NotImplementedError()

    def add_user_license(self, username, license_name):
        raise NotImplementedError()

    def request_api_key(username, license_name):
        raise NotImplementedError()

    def activate_api_key(username, api_key, activation_info):
        raise NotImplementedError()

    def add_temp_user(self, username, password, email, phone_number, permission_level):
        raise NotImplementedError()

    def verify_temp_user_and_add(self, username, session_id, mfa_code):
        raise NotImplementedError()









