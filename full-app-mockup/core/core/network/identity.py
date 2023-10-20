"""
Identity module

Purpose:

- Query the identity/API server for a list of all nodes in the network.
- Periodically query the identity server for updates
- Register current node, if necessary, with API key
- Define role for current node based on whether it's admin or not
- Generate/access local secret keys (or access remote-stored secret keys)

"""

import json


class Identity:
    def __init__(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.port = self.config["docker_port"]
        self.hostname = self.config["hostname"]
        self.lan_ip_address = self.config.get("lan_ip_address",None)
        self.wan_ip_address = self.config.get("wan_ip_address", None)
        self.role = self.config["role"]
        self.private_key = self.config["private_key"]
        self.public_key = self.config["public_key"]

        self.database_host = self.config["database_host"]
        self.database_port = int(self.config["database_port"])
        self.database_name = self.config["database_name"]

        self.zmq_port = self.config.get("zmq_port", None)
        self.zmq_host = self.config.get("zmq_host", None)



