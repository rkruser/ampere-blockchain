import zmq
import time
from multiprocessing import Process, Value, Lock
import sys
import random
import threading
from client import login_or_register, register_public_key, download_node_database, logout_and_close
from utils import get_lan_ip

def get_active_clients_list(name, port, clients):
    active_clients = []
    for client in clients.values():
        client.send(b"ping from " + name.encode()+ b':' + str(port).encode())
        try:
            response = client.recv()
            if name.startswith("node0"):
                print(f"Node {name}:{port} received {response.decode()}")
            active_clients.append(client)
        except zmq.error.Again:
            if name.startswith("node0"):
                print(f"Node {name}:{port} timed out on {client}")
    return active_clients

def send_random_pings(name, port, active_clients):
    t1 = time.time()
    t2 = t1

    while len(active_clients) > 0 and t2-t1 < 30:
        client = random.choice(active_clients)
        client.send(b"ping from " + name.encode() + b':' + str(port).encode())
        try:
            response = client.recv()
            if name.startswith("node0"):
                print(f"Node {name}:{port} received {response.decode()}")
        except zmq.error.Again:
            pass

        time.sleep(random.randint(1, 5))
        t2 = time.time()

def receive_messages(name, port, server, lock, counter):
    t1 = time.time()
    t2 = t1
    while t2-t1 < 50:
        try:
            address, response = server.recv_multipart()
            server.send_multipart([address, b"pong from " + name.encode() + b':' + str(port).encode()])
            if name.startswith("node0"): 
                print(f"Node {name}:{port} received {response.decode()}")
            with lock:
                counter.value += 1
        except zmq.error.Again:
            pass
        finally:
            t2 = time.time()

# Each process will call this function with a unique port
def run_node(name, lock, counter):
    password = name

    ctx = zmq.Context()
    public_key, secret_key = zmq.curve_keypair()

    # Setup server socket
    server = ctx.socket(zmq.ROUTER)
    server.setsockopt(zmq.RCVTIMEO, 2000)
    server.setsockopt(zmq.LINGER, 0)
    server.curve_secretkey = secret_key
    server.curve_publickey = public_key
    server.curve_server = True

    # Set random port in range 5555-6555
    port = random.randint(5555, 6555)
    port_not_bound = True
    my_ip_address = get_lan_ip()
    count = 0
    while port_not_bound and count < 10:
        try:
            server.bind(f"tcp://{my_ip_address}:{port}")
            port_not_bound = False
        except Exception as e:
            print(e)
            port = random.randint(5555, 6555)
            count += 1
    if port_not_bound:
        print("Failed to bind port, exiting")
        exit(1)

    session = login_or_register(name, password)                                                         
    api_key_hash = register_public_key(session, public_key.decode('ascii'), port, lan_ip=my_ip_address)
    time.sleep(1)
    node_database = download_node_database(session)
    logout_and_close(session)

    if name.startswith("node0"):
        print(node_database)

    del node_database[api_key_hash] #Get rid of self

    # Setup client sockets for all other nodes
    clients = {}
    for keyhash, info in node_database.items():
        client = ctx.socket(zmq.DEALER)
        client.setsockopt(zmq.LINGER, 0)
        client.setsockopt(zmq.RCVTIMEO, 1000) # millisecond timeout
        client.curve_secretkey = secret_key
        client.curve_publickey = public_key
        client.curve_serverkey = info["public_key"].encode('ascii')
        client_port = info["port"]
        client_ip = info["lan_ip_address"]
        client.connect(f"tcp://{client_ip}:{client_port}")
        clients[keyhash] = client

    receive_thread = threading.Thread(target=receive_messages, args=(name, port, server, lock, counter))
    receive_thread.start()

    active_clients = get_active_clients_list(name, port, clients)
    if name.startswith("node0"):
        print("active_clients: ", active_clients)

    ping_thread = threading.Thread(target=send_random_pings, args=(name, port, active_clients))
    ping_thread.start()

    ping_thread.join()
    receive_thread.join()

    # # Sending pings
    # for _, client in clients.items():
    #     client.send(b"ping from " + name.encode()+ b':' + str(port).encode())

    # # Waiting for responses
    # for _ in [keyhash for keyhash in node_database if keyhash != api_key_hash]:
    #     try:
    #         _, response = server.recv_multipart()
    #         print(f"Node {name}:{port} received {response.decode()}")
    #         with lock:
    #             counter.value += 1
    #     except zmq.error.Again:
    #         print(f"Node {name}:{port} timed out")
    #         break
    #     except Exception as e:
    #         print(f"Node on port {port} error receiving response: {e}")

    # Cleanup
    server.close()
    for client in clients.values():
        client.close()

    ctx.term()

def main(N):
    counter = Value('i', 0)
    lock = Lock()
    processes = []
    name_append = random.randint(0,100000) #so we don't have to restart server
    for i in range(N):
        p = Process(target=run_node, args=("node"+str(i)+'_'+str(name_append), lock, counter))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"Total ping count: {counter.value}")

if __name__ == "__main__":
    print(sys.argv)
    N = int(sys.argv[1])
    main(N)
