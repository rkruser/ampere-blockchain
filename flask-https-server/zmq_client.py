import zmq
import time
from multiprocessing import Process, Value, Lock
import sys

def build_database(N):
    ctx = zmq.Context()
    port = 5555
    database = {}

    while len(database) < N:
        try:
            # Try to bind to the port to check its availability
            temp_socket = ctx.socket(zmq.REP)
            temp_socket.bind(f"tcp://*:{port}")
            temp_socket.close()  # Close immediately after successful bind

            # Generate a CurveZMQ keypair for the available port
            public_key, secret_key = zmq.curve_keypair()
            database[port] = {
                "public_key": public_key.decode('ascii'),
                "secret_key": secret_key.decode('ascii')
            }

        except zmq.ZMQError:
            # Port is not available, skip it
            pass

        # Move on to the next port
        port += 1

    ctx.term()
    return database

# Each process will call this function with a unique port
def run_node(port, public_key, secret_key, database, counter, lock):
    ctx = zmq.Context()

    # Setup server socket
    server = ctx.socket(zmq.ROUTER)
    server.curve_secretkey = secret_key.encode('ascii')
    server.curve_publickey = public_key.encode('ascii')
    server.curve_server = True
    server.bind(f"tcp://127.0.0.1:{port}")

    # Setup client sockets for all other nodes
    clients = {}
    for other_port, keys in database.items():
        if other_port == port:
            continue
        client = ctx.socket(zmq.DEALER)
        client.curve_secretkey = secret_key.encode('ascii')
        client.curve_publickey = public_key.encode('ascii')
        client.curve_serverkey = keys["public_key"].encode('ascii')
        client.connect(f"tcp://127.0.0.1:{other_port}")
        clients[other_port] = client

    # Sending pings
    for other_port, client in clients.items():
        client.send(b"ping from " + str(port).encode())

    # Waiting for responses
    for _ in [p for p in database if p != port]:
        try:
            address, response = server.recv_multipart()
            print(f"Node on port {port} received {response.decode()}")
            with lock:
                counter.value += 1
        except Exception as e:
            print(f"Node on port {port} error receiving response: {e}")

    # Cleanup
    server.close()
    for client in clients.values():
        client.close()
    
    ctx.term()

def main(DATABASE):
    counter = Value('i', 0)
    lock = Lock()
    processes = []
    for port, keys in DATABASE.items():
        p = Process(target=run_node, args=(port, keys["public_key"], keys["secret_key"], 
                                           DATABASE, counter, lock))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"Total ping count: {counter.value}")

if __name__ == "__main__":
    print(sys.argv)
    N = int(sys.argv[1])
    DATABASE = build_database(N)
    print(DATABASE)
    main(DATABASE)
