"""
Connection module

Purpose:

- Establish connection to other nodes in the network (using ZMQ, or whatever)
- Maintain threads/processes for each connection, so as not to slow down main process
- Send/receive messages to/from other nodes
- If admin, push/pull data from other nodes
- If not admin, only pull data from other nodes
- Provide functions to communicate with the network of nodes (e.g. through message passing to the network threads)

"""