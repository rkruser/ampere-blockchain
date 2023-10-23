from flask import Flask, request, jsonify
from worker_node import start_node
import multiprocessing
import time

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

        try:
            process.terminate()
            del subprocesses[node_name]
            del address_table[node_name]
        except Exception as e:
            return jsonify({"error": f"Error terminating node {node_name}: {e}"}), 500
        
        return jsonify({"message": f"Node {node_name} terminated!"}), 200

    @app.route('/list_nodes', methods=['GET'])
    def list_nodes():
        active_statuses = {node_name: address for node_name, address in address_table.items()}
        #active_statuses = {'abc': (1,2,3), 'cde': (4,5,6), 'efg': (7,8,9)}
        return jsonify(active_statuses)
    
    @app.route('/post_address_table', methods=['POST'])
    def post_address_table():
        if 'address_table' not in request.json:
            return jsonify({"error": "Address table is required!"}), 400
        new_address_table = request.json.get('address_table')
        address_table.clear()
        address_table.update(new_address_table)
        return jsonify({"message": "Address table updated!"}), 200

    return app

def run_app(subprocesses, address_table):
    app = make_app(subprocesses, address_table)
    app.run(port=5000)

if __name__ == "__main__":
    #manager = multiprocessing.Manager()
    subprocesses = {}
    address_table = {}
    
    app_process = multiprocessing.Process(target=run_app, args=(subprocesses, address_table))
    app_process.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        app_process.terminate()
        for proc in subprocesses.values():
            proc.terminate()
        exit(0)