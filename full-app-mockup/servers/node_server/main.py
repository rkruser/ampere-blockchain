from flask import Flask, request, jsonify
#import subprocess
import multiprocessing
import zmq
import time
from worker_node import start_node

NODE_PROGRAM_PATH = 'worker_node.py'  # replace with the path to the node code
LISTEN_PORT = 8000  # Change the port number if needed

class NodeManager:
    def __init__(self, address_table):
        self.address_table = address_table

    def ping_nodes(self):
        context = zmq.Context()

        while True:
            time.sleep(10)
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

    def incoming_listener(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{LISTEN_PORT}")  # Replace with the port you want to listen on

        while True:
            message = socket.recv_string()
            node_name, content = message.split(':')

            print(f"Received message from {node_name}: {content}")

            if node_name in self.address_table:
                # Do something based on the node_name
                socket.send_string("Message received")


def make_app(subprocesses, address_table):
    app = Flask(__name__)
    @app.route('/make_node', methods=['POST'])
    def make_node():
        node_name = request.json.get('node_name')
        node_ip = request.json.get('node_ip')
        node_port = request.json.get('node_port')
        if not node_name or not node_ip or not node_port:
            return jsonify({"error": "Insufficient node info!"}), 400

        if node_name in subprocesses:
            return jsonify({"error": f"Node {node_name} already exists!"}), 400
        
        #process = subprocess.Popen(['python', NODE_PROGRAM_PATH, node_name, node_ip, node_port])
        process = multiprocessing.Process(target=start_node, args=(node_name, node_ip, node_port))
        process.start()

        subprocesses[node_name] = process
        address_table[node_name] = (node_ip, node_port, True)
        
        return jsonify({"message": f"Node {node_name} created!"}), 200

    @app.route('/delete_node', methods=['POST'])
    def delete_node():
        node_name = request.json.get('node_name')
        if not node_name:
            return jsonify({"error": "Node name is required!"}), 400

        process = subprocesses.get(node_name)
        if not process:
            return jsonify({"error": f"No such node: {node_name}"}), 404

        process.terminate()
        del subprocesses[node_name]
        del address_table[node_name]
        
        return jsonify({"message": f"Node {node_name} terminated!"}), 200

    @app.route('/list_nodes', methods=['GET'])
    def list_nodes():
        active_statuses = {node_name: address for node_name, address in address_table.items()}
        return jsonify(active_statuses)

    return app

def run_app(subprocesses, address_table):
    app = make_app(subprocesses, address_table)
    app.run(port=5000)

if __name__ == "__main__":
    subprocesses = {}  # {node_name: subprocess_object}

# Shared dictionary for address_table
    manager = multiprocessing.Manager()
    address_table = manager.dict()  # {name: (IP address, port, active_status)}
    
    node_manager = NodeManager(address_table)
    p1 = multiprocessing.Process(target=node_manager.ping_nodes)
    p2 = multiprocessing.Process(target=node_manager.incoming_listener)

    p1.start()
    p2.start()

    p3 = multiprocessing.Process(target=run_app, args=(subprocesses, address_table))
    p3.start()

    try:
        while True:
                time.sleep(10)
                print("Address table:", address_table)
    except KeyboardInterrupt:
        print("Exiting...")
        p1.terminate()
        p2.terminate()
        p3.terminate()
        for process in subprocesses.values():
            process.terminate()
        exit(0)
