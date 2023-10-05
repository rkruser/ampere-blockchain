import security as sec
import time

_invitation_database = set()
_user_database = {}
_session_database = {}
_api_key_database = {}

# The license a user has purchased or is given, which defines
#  the features they have access to,
#  in this case, how many API keys they can generate
license_database = {
    "standard_license": 1,
    "special_license": 2
}

node_database = {}

def add_invitation(invitation_code):
    _invitation_database.add(invitation_code)
    return True

def revoke_invitation(invitation_code):
    _invitation_database.remove(invitation_code)
    return True

def verify_invitation(invitation_code):
    return invitation_code in _invitation_database

def add_user(username, password, permission_level="user"):
    if username in _user_database:
        raise ValueError("User already exists")
    salt = sec.generate_salt()
    password_hash = sec.hash_password(password, salt)
    _user_database[username] = {
        "salt": salt,
        "password_hash": password_hash,
        "ip_sessions": {},
        "licenses": {
            "standard_license": set()
        },
        "permissions": permission_level
    }
    return True

def has_admin_permissions(username):
    if username not in _user_database:
        raise ValueError("Invalid username")
    return _user_database[username]["permissions"] == "admin"

def change_user_password(username, password):
    if username not in _user_database:
        raise ValueError("Invalid username")
    salt = sec.generate_salt()
    password_hash = sec.hash_password(password, salt)
    _user_database[username]["salt"] = salt
    _user_database[username]["password_hash"] = password_hash
    return True

def login_user(username, password, ip_address):
    if username not in _user_database:
        raise ValueError("Invalid username")
    salt = _user_database[username]["salt"]
    password_hash = _user_database[username]["password_hash"]
    if not sec.verify_password(password, salt, password_hash):
        raise ValueError("Invalid password")
    return create_user_session_key(username, ip_address)

def logout_user(session_key):
    if session_key not in _session_database:
        return False
    username = _session_database[session_key]["username"]
    ip_address = _session_database[session_key]["ip_address"]
    user_sessions = _user_database[username]["ip_sessions"]
    if ip_address in user_sessions:
        del user_sessions[ip_address]
    del _session_database[session_key]
    return True

def remove_user(username):
    if username not in _user_database:
        raise ValueError("Invalid username")
    # remove all user sessions
    user_sessions = _user_database[username]["ip_sessions"]
    for ip_address in list(user_sessions.keys()):
        session_key = user_sessions[ip_address]
        if session_key in _session_database:
            del _session_database[session_key]
    # remove all user API keys
    user_licenses = _user_database[username]["licenses"]
    for license_name in user_licenses:
        for api_key in list(user_licenses[license_name]):
            if api_key in _api_key_database:
                del _api_key_database[api_key]
    del _user_database[username]
    return True

def remove_timed_out_user_sessions(username):
    user_sessions = _user_database[username]["ip_sessions"]
    for ip_address in list(user_sessions.keys()):
        session_key = user_sessions[ip_address]
        if session_key not in _session_database:
            del user_sessions[ip_address]
        elif _session_database[session_key]["expiration"] < time.time():
            del user_sessions[ip_address]
            del _session_database[session_key]


def create_user_session_key(username, ip_address, duration=3600):
    remove_timed_out_user_sessions(username)
    user_sessions = _user_database[username]["ip_sessions"]
    if ip_address not in user_sessions:
        if len(user_sessions) >= 10:
            raise ValueError("Too many active sessions for this user")
    else:
        old_session_key = user_sessions[ip_address]
        if old_session_key in _session_database:
            del _session_database[old_session_key]
        del user_sessions[ip_address]

    session_key = sec.generate_session_key()
    _session_database[session_key] = {
        "username": username,
        "ip_address": ip_address,
        "expiration": time.time() + duration,
    }
    user_sessions[ip_address] = session_key
    return session_key


def verify_session_key(ip_address, session_key):
    if session_key not in _session_database:
        return None
    username = _session_database[session_key]["username"]
    remove_timed_out_user_sessions(username)
    # If statement replicated twice: inelegant
    if session_key not in _session_database:
        return None
    if _session_database[session_key]["ip_address"] != ip_address:
        return None
    return username


def add_user_license(username, license_name):
    if license_name not in license_database:
        raise ValueError("Invalid license name")
    if license_name not in _user_database[username]["licenses"]:
        _user_database[username]["licenses"][license_name] = set()
    else:
        raise ValueError("User already has this license")
    return True


def remove_user_expired_nonactivated_api_keys(username):
    user_licenses = _user_database[username]["licenses"]
    for license_name in user_licenses:
        for api_key in list(user_licenses[license_name]):
            if api_key not in _api_key_database:
                user_licenses[license_name].remove(api_key)
            elif _api_key_database[api_key]["activation_expiration"] < time.time():
                if not _api_key_database[api_key]["activated"]:
                    user_licenses[license_name].remove(api_key)
                    del _api_key_database[api_key]


def request_api_key(username, license_name):
    remove_user_expired_nonactivated_api_keys(username)
    avaliable_licenses = _user_database[username]["licenses"]
    if license_name not in avaliable_licenses:
        raise ValueError("User does not have this license")
    if len(avaliable_licenses[license_name]) >= license_database[license_name]:
        raise ValueError("User has reached the maximum number of API keys for this license")
    api_key = sec.generate_api_key()
    _api_key_database[api_key] = {
        "creator_username": username,
        "activator_username": None,
        "license_name": license_name,
        "activated": False,
        "activation_expiration": time.time() + 86400
    }
    avaliable_licenses[license_name].add(api_key)
    return api_key


def activate_api_key(username, api_key, data=None):
    if api_key not in _api_key_database:
        raise ValueError("Invalid API key")
    if _api_key_database[api_key]["activated"]:
        raise ValueError("API key already activated")
    if _api_key_database[api_key]["activation_expiration"] < time.time():
        raise ValueError("API key activation period has expired")
    if data is None:
        raise ValueError("No activation data provided")
    _api_key_database[api_key]["activated"] = True
    _api_key_database[api_key]["activator_username"] = username
    ip_address = data["ip_address"]
    port = data["port"]
    public_key = data["public_key"]
    api_key_hash = sec.hash_api_key_truncate_64(api_key)
    node_database[api_key_hash] = {
        "username": username,
        "ip_address": ip_address,
        "port": port,
        "public_key": public_key
    }

    return True



def convert_sets_to_lists(data):
    if isinstance(data, set):
        return list(data)
    elif isinstance(data, dict):
        return {key: convert_sets_to_lists(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_sets_to_lists(value) for value in data]
    else:
        return data
