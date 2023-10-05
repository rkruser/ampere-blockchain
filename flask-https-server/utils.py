import socket
import requests
import random

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually establish a connection, just retrieves the local endpoint address
        s.connect(('10.255.255.255', random.randint(1,65000)))  # Use an arbitrary IP address to determine the most appropriate network interface
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'
    finally:
        s.close()
    return ip_address

def get_remote_ip():
    try:
        response = requests.get('https://httpbin.org/ip')
        return response.json()['origin']
    except requests.RequestException:
        print("Error: Unable to fetch external IP.")
        return None


