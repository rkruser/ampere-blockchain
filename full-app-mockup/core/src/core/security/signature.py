"""
Digital signature info
"""

class Signature:
    def __init__(self):
        self.signature_timestamp = None
        self.signer_unique_name = None
        self.signer_notes = None
        self.signature = None

    def byte_serialize(self):
        pass

    def string_serialize(self):
        pass


"""
Images/scans of patient signed documents authorizing app use?
"""
class Proof:
    pass


class AuthenticatedEncryption:
    def __init__(self):
        self.mac = None
        self.message = None
        self.size = None