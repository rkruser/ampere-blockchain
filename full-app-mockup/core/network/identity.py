"""
Identity module

Purpose:

- Query the identity/API server for a list of all nodes in the network.
- Periodically query the identity server for updates
- Register current node, if necessary, with API key
- Define role for current node based on whether it's admin or not
- Generate/access local secret keys (or access remote-stored secret keys)

"""