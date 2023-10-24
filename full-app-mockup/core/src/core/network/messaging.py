"""
Code for signed messages
"""

# Idea: Subscription model
#  Nodes can subscribe to receive updates on the blockchains of particular patients, or updates on other info
#  All nodes are subscribed to the main chain


class Message:
    def read_from_serial(self):
        pass

    def serialize(self):
        pass

    def verify_message(self):
        pass


class OuterMessage(Message):
    def __init__(self):
        self.message_hash = None
        self.sender_signature = None

class InnerMessage(Message):
    def __init__(self):
        self.protocol_name = None
        self.protocol_version = None
        self.protocol_state = None
        self.nonce = None
        self.round_number = None
        self.sender_name = None
        self.message_timestamp = None
        self.message_data = None

class MessageData(Message):
    def __init__(self):
        self.size = None
        self.format = None
        self.format_version = None
        self.data = None

