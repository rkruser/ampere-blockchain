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