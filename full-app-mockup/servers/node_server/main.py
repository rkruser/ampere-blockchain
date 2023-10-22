import multiprocessing
import time
#from gunicorn.app.base import BaseApplication
from app import make_app
from manager import NodeManager  # Assume NodeManager is in its own module

# class StandaloneApplication(BaseApplication):
#     def __init__(self, app, options=None):
#         self.application = app
#         self.options = options or {}
#         super().__init__()

#     def load_config(self):
#         config = {key: value for key, value in self.options.items()
#                   if key in self.cfg.settings and value is not None}
#         for key, value in config.items():
#             self.cfg.set(key.lower(), value)

#     def load(self):
#         return self.application

# def run_gunicorn(subprocesses, address_table):
#     options = {
#         'bind': '0.0.0.0:5000',
#         'workers': 4  # Adjust the number of workers as needed
#     }
#     StandaloneApplication(make_app(subprocesses, address_table), options).run()

def run_app(subprocesses, address_table):
    app = make_app(subprocesses, address_table)
    app.run(port=5000)

if __name__ == "__main__":
    subprocesses = {}

    manager = multiprocessing.Manager()
    address_table = manager.dict()

    node_manager = NodeManager(address_table)
    p1 = multiprocessing.Process(target=node_manager.ping_nodes)
    p2 = multiprocessing.Process(target=node_manager.incoming_listener)
    p3 = multiprocessing.Process(target=run_app, args=(subprocesses, address_table))

    p1.start()
    p2.start()
    p3.start()

    try:
        while True:
            time.sleep(10)
            print("Address table:", address_table)
    except KeyboardInterrupt:
        print("Exiting...")
        p1.terminate()
        p2.terminate()
        for process in subprocesses.values():
            process.terminate()
        exit(0)
