from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os


def get_salted_kdf(salt, key_byte_length=32):
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_byte_length,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

def hash_password(password_string, salt_hex):
    kdf = get_salted_kdf(bytes.fromhex(salt_hex))
    return kdf.derive(password_string.encode()).hex()


def random_bytes(length=32):
    return os.urandom(length)

def generate_salt(byte_length=32):
    return random_bytes(byte_length).hex()

def generate_session_key(byte_length=16):
    return random_bytes(byte_length).hex()

def generate_api_key(byte_length=16):
    return random_bytes(byte_length).hex()

def verify_password(password_string, salt_hex, stored_password_hash_hex):
    salt = bytes.fromhex(salt_hex)
    stored_password_hash = bytes.fromhex(stored_password_hash_hex)
    kdf = get_salted_kdf(salt)
    try:
        kdf.verify(password_string.encode(), stored_password_hash)
    except ValueError as e:
        print(e)
        return False
    return True