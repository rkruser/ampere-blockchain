import zmq
import time
from multiprocessing import Process, Value, Lock
import sys
import random
from client import login_or_register, register_public_key, download_node_database, logout_and_close
from utils import get_lan_ip

# Each process will call this function with a unique port
def run_node(name, lock, counter):
    password = name

    ctx = zmq.Context()
    public_key, secret_key = zmq.curve_keypair()

    # Setup server socket
    server = ctx.socket(zmq.ROUTER)
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

    time.sleep(random.random())
    session = login_or_register(name, password)                                                         
    api_key_hash = register_public_key(session, public_key.decode('ascii'), port, lan_ip=my_ip_address)
    time.sleep(5)
    node_database = download_node_database(session)
    logout_and_close(session)

    if name.startswith("node0"):
        print(node_database)

    # Setup client sockets for all other nodes
    clients = {}
    for other_keyhash, info in node_database.items():
        if other_keyhash == api_key_hash:
            continue
        client = ctx.socket(zmq.DEALER)
        client.curve_secretkey = secret_key
        client.curve_publickey = public_key
        client.curve_serverkey = info["public_key"].encode('ascii')
        client_port = info["port"]
        client_ip = info["lan_ip_address"]
        client.connect(f"tcp://{client_ip}:{client_port}")
        clients[other_keyhash] = client

    # Sending pings
    for _, client in clients.items():
        client.send(b"ping from " + name.encode()+ b':' + str(port).encode())

    # Waiting for responses
    server.setsockopt(zmq.RCVTIMEO, 5000)
    for _ in [keyhash for keyhash in node_database if keyhash != api_key_hash]:
        try:
            _, response = server.recv_multipart()
            print(f"Node {name}:{port} received {response.decode()}")
            with lock:
                counter.value += 1
        except zmq.error.Again:
            print(f"Node {name}:{port} timed out")
            break
        except Exception as e:
            print(f"Node on port {port} error receiving response: {e}")

    # Cleanup
    server.setsockopt(zmq.LINGER, 0)
    server.close()
    for client in clients.values():
        client.setsockopt(zmq.LINGER, 0)
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
