import requests

def make_node(node_name, node_ip, node_port):
    # URL for your Flask app
    url = "http://127.0.0.1:5000/make_node"  # Adjust the endpoint as needed

    # Data to be sent in the POST request
    data = {
        'node_name': node_name,
        'node_ip': node_ip,
        'node_port': node_port
    }

    # Make the POST request
    response = requests.post(url, json=data)

    # Print the response
    print(response.status_code)
    print(response.json())

def delete_node(node_name):
    # URL for your Flask app
    url = "http://127.0.0.1:5000/delete_node"  # Adjust the endpoint as needed

    # Data to be sent in the POST request
    data = {
        'node_name': node_name,
    }

    # Make the POST request
    response = requests.post(url, json=data)

    # Print the response
    print(response.status_code)
    print(response.json())

def list_nodes():
    url = "http://127.0.0.1:5000/list_nodes"
    response = requests.get(url)
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    while True:
        option = input("m=make node, d=delete node, l=list nodes, q=quit: ")
        if option == "m":
            node_name = input("Enter node name: ")
            node_ip = "127.0.0.1"
            node_port = input("Enter node port: ")
            node_port = 9000+int(node_port)
            make_node(node_name, node_ip, node_port)
        elif option == "d":
            node_name = input("Enter node name: ")
            delete_node(node_name)
        elif option == "l":
            list_nodes()
        elif option == "q":
            break
        else:
            print("Invalid option!")