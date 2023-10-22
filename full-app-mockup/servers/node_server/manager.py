import zmq
import time
import requests
import threading
LISTEN_PORT = 8010  # Change the port number if needed

class NodeManager:
    def __init__(self, address_table=None):
        if address_table is None:
            self.use_requests = True
            self.address_table = {}
        else:
            self.address_table = address_table
            self.use_requests = False

    def ping_nodes(self):
        context = zmq.Context()

        while True:
            time.sleep(1)
            if self.use_requests:
                url = "http://127.0.0.1:5000/list_nodes"
                response = requests.get(url)
                print(response.json())
                print(type(response.json()))
                self.address_table = response.json()

            nodes = list(self.address_table.keys())

            print("Pinging nodes:", nodes)

            for node in nodes:
                ip, port, _ = self.address_table[node]
                socket = context.socket(zmq.REQ)
                socket.connect(f"tcp://{ip}:{port}")
                socket.send_string("ping")

                try:
                    socket.setsockopt(zmq.RCVTIMEO, 1000)  # Set timeout to 1 second (1000 milliseconds)
                    response = socket.recv_string()
                    if response == "pong":
                        self.address_table[node] = (ip, port, True)
                except zmq.ZMQError:
                    print("Node", node, "is not responding")
                    self.address_table[node] = (ip, port, False)

            if self.use_requests:
                url = "http://127.0.0.1:5000/post_address_table"
                response = requests.post(url, json={'address_table':self.address_table})
                print(response.json())
            
            time.sleep(10)

    def incoming_listener(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{LISTEN_PORT}")  # Replace with the port you want to listen on

        while True:
            message = socket.recv_string()
            node_name, content = message.split(':')

            print(f"Received message from {node_name}: {content}")
            socket.send_string("Message received")


if __name__ == "__main__":
    import sys
    address_table = None
    if len(sys.argv) > 1:
        address_table = {"asdf":("127.0.0.1",9001,True)}
    node_manager = NodeManager(address_table=address_table)
    p1 = threading.Thread(target=node_manager.ping_nodes)
    p1.daemon = True
    p2 = threading.Thread(target=node_manager.incoming_listener)
    p2.daemon = True
    p1.start()
    p2.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)