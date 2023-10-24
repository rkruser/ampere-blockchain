"""
Core logic of the blockchain
"""


class Block:
    def byte_serialize():
        pass
    def read_bytes():
        pass
    def ai_serialize():
        pass
    def readable_serialize():
        pass
    def block_hash():
        pass

class OuterBlock(Block):
    def __init__(self):
        self.inner_block_hash = None
        self.proposer_node_signature = None
        self.proposer_user_signature = None # Signature of user account that made the block (seems like a good idea)
        self.verifier_signatures = None
        self.inner_block = None

class InnerBlock(Block):
    def __init__(self):
        self.block_type = None
        self.block_version = None
        self.protocol_version = None
        self.block_timestamp = None
        self.block_number = None #How would this work? (Necessary though to maintain global agreement on most recent block)
        self.nonce = None # Is this necessary?
        self.prev_blockhash = None # Hash of most recent block in central chain
        self.precursors = None # Prefix notation computation description for current block
        self.data_manifest = None
        self.data = None

class DataBlock(Block):
    def __init__(self):
        self.format = None
        self.format_version = None
        self.size = None
        self.data = None


"""
Class for holding an entire blockchain (multiple outer blocks) and manipulating it
"""
class Blockchain:
    def __init__(self):
        self.encryption_scheme = None
        self.all_block_data = None
        self.blockchain_id = None
        self.patient_identifying_info = None