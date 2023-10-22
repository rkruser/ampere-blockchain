import zmq
import time
import threading
import random
import string
import sys

NODE_MANAGER_ADDRESS = "127.0.0.1"  # Replace with the Node Manager's address
NODE_MANAGER_PORT = 8010  # Replace with the Node Manager's port

class Node:
    def __init__(self, node_name, node_ip, node_port):
        self.node_name = node_name
        self.node_ip = node_ip
        self.node_port = node_port

    def listen_for_pings(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{self.node_port}")  # Replace with the port the node listens on

        while True:
            print(f"{self.node_name} listening for pings")
            message = socket.recv_string()
            if message == "ping":
                socket.send_string("pong")

    def send_random_strings(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect(f"tcp://{NODE_MANAGER_ADDRESS}:{NODE_MANAGER_PORT}")  # Replace with the Node Manager's address and port

        while True:
            time_to_wait = random.uniform(5, 10)
            time.sleep(time_to_wait)
            print(f"{self.node_name} Sending message")

            random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=10))  # 10-character random string
            message = f"{self.node_name}:{random_str}"
            socket.send_string(message)
            response = socket.recv_string()  # This assumes the node manager sends a response (like "Message received")


def start_node(node_name, node_ip, node_port):
    node = Node(node_name, node_ip, node_port)
    t1 = threading.Thread(target=node.listen_for_pings)
    t1.daemon = True
    t2 = threading.Thread(target=node.send_random_strings)
    t2.daemon = True
    t1.start()
    t2.start()

    try:
        while True:
            print(f"{node_name} is running")
            time.sleep(10)
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    node_name = sys.argv[1]
    node_port = sys.argv[2]

    start_node(node_name, "127.0.0.1", node_port)