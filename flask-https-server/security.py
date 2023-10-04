from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey
import os
import base64

# Encode is bytes to string
# Decode is string to bytes
ENCODING_SCHEMES = {
    'hex': {
        'encode': lambda x: x.hex(),
        'decode': lambda x: bytes.fromhex(x),
    },
    'base64': {
        'encode': lambda x: base64.b64encode(x).decode(),
        'decode': lambda x: base64.b64decode(x.encode()),
    },
    'base32': {
        'encode': lambda x: base64.b32encode(x).decode(),
        'decode': lambda x: base64.b32decode(x.encode()),
    },
    'base64_urlsafe': {
        'encode': lambda x: base64.urlsafe_b64encode(x).decode(),
        'decode': lambda x: base64.urlsafe_b64decode(x.encode()),
    },
    'binary': {
        'encode': lambda x: x,
        'decode': lambda x: x,
    }
}

class EncodingScheme:
    def __init__(self, encode_func, decode_func):
        self.encode_func = encode_func
        self.decode_func = decode_func

    def encode(self, data):
        return self.encode_func(data)

    def decode(self, data):
        return self.decode_func(data)

class EncodingSchemes:
    pass

for scheme, funcs in ENCODING_SCHEMES.items():
    setattr(EncodingSchemes, scheme, EncodingScheme(funcs['encode'], funcs['decode']))

DEFAULT_SCHEME = EncodingSchemes.base64_urlsafe

def set_default_encoding_scheme(scheme):
    DEFAULT_SCHEME = getattr(EncodingSchemes, scheme)


def get_salted_kdf(salt, key_byte_length=32):
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_byte_length,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

def hash_password(password_string, encoded_salt, scheme=DEFAULT_SCHEME):
    kdf = get_salted_kdf(scheme.decode(encoded_salt))
    return scheme.encode(kdf.derive(password_string.encode()))

def random_bytes(length=32):
    return os.urandom(length)

def generate_salt(byte_length=32, scheme=DEFAULT_SCHEME):
    return scheme.encode(random_bytes(byte_length))

def generate_session_key(byte_length=16, scheme=DEFAULT_SCHEME):
    return scheme.encode(random_bytes(byte_length))

def generate_api_key(byte_length=16, scheme=EncodingSchemes.hex):
    return scheme.encode(random_bytes(byte_length))

def verify_password(password_string, encoded_salt, encoded_stored_password_hash, scheme=DEFAULT_SCHEME):
    salt = scheme.decode(encoded_salt)
    stored_password_hash = scheme.decode(encoded_stored_password_hash)
    kdf = get_salted_kdf(salt)
    try:
        kdf.verify(password_string.encode(), stored_password_hash)
    except InvalidKey as e:
        print(e)
        return False
    return True