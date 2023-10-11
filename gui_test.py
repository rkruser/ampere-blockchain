import tkinter as tk
from multiprocessing import Process, Queue
import time

def gui_process(queue):
    def submit1():
        text = field1.get()
        queue.put(("field1", text))
    
    def submit2():
        text = field2.get()
        queue.put(("field2", text))

    # GUI setup
    window = tk.Tk()
    window.title("TKinter GUI")

    # Field 1
    field1 = tk.Entry(window)
    field1.pack(padx=10, pady=5)
    btn1 = tk.Button(window, text="Submit 1", command=submit1)
    btn1.pack(padx=10, pady=5)

    # Field 2
    field2 = tk.Entry(window)
    field2.pack(padx=10, pady=5)
    btn2 = tk.Button(window, text="Submit 2", command=submit2)
    btn2.pack(padx=10, pady=5)

    window.mainloop()

def main_process():
    queue = Queue()

    # Start GUI in separate process
    p = Process(target=gui_process, args=(queue,))
    p.start()

    # Listen for messages from the GUI
    while True:
        if not queue.empty():
            field, value = queue.get()
            print(f"Received from {field}: {value}")

            if value == 'quit':
                print("Quittin main print loop; waiting for GUI to close")
                break

        time.sleep(0.0166) #1/60th of a second, truncated

    p.join()

if __name__ == '__main__':
    main_process()
