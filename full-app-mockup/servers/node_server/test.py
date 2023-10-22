import requests

# URL for your Flask app
url = "http://127.0.0.1:5000/make_node"  # Adjust the endpoint as needed

# Data to be sent in the POST request
data = {
    'node_name': 'node1',
    'node_ip': '127.0.0.1',
    'node_port': '9001'
}

# Make the POST request
response = requests.post(url, json=data)

# Print the response
print(response.status_code)
print(response.json())
