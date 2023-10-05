import requests
import time
import json

from utils import get_lan_ip, get_remote_ip

base_url = "https://ryenandvivekstartup.online"
login_url = base_url + "/login"
home_url = base_url + "/home"
logout_url = base_url + "/logout"
register_url = base_url + "/register"
server_status_url = base_url + "/server_status"
add_user_license_url = base_url + "/add_user_license"
request_api_key_url = base_url + "/request_api_key"
activate_api_key_url = base_url + "/activate_api_key"
download_node_database_url = base_url + "/get_node_database"

create_account = None
username = None
password = None
client_number = None



def login_and_register_public_key(user, passw, public_key, port):
    session = requests.Session()

    data = {
        "username": user,
        "password": passw
    }
    response = session.post(login_url, json=data)
    if response.status_code != 200:
        registration_data = data.copy()
        registration_data["invitation_code"] = "basic_invite"
        response = session.post(register_url, json=registration_data)
        if response.status_code != 200:
            print("Registration failed")
            exit(1)
        response = session.post(login_url, json=data)
        if response.status_code != 200:
            print("Login failed")
            exit(1)

    response = session.post(request_api_key_url, json={"license_name": "standard_license"})
    if response.status_code != 200:
        print("Request API key failed")
        exit(1)
    api_key = response.json().get("api_key", None)
    api_key_hash = response.json().get("api_key_hash", None)

    activation_data = {
        "api_key": api_key,
        "node_port": port,
        "public_key": public_key,
        "lan_ip_address": get_lan_ip(),
        "remote_ip_address": get_remote_ip(),
    }
    response = session.post(activate_api_key_url, json=activation_data)
    if response.status_code != 200:
        print("Activation failed")
        exit(1)
    print(response.json().get("message", ""))

    return session, api_key_hash

def download_node_database(session):
    response = session.get(download_node_database_url)
    if response.status_code != 200:
        print("Download node database failed")
        exit(1)
    return response.json().get("node_database", None)

def logout_and_close(session):
    response = session.get(logout_url)
    session.close()
    if response.status_code != 200:
        print("Logout failed")
        exit(1)

def client5():
    session, _ = login_and_register_public_key(username, password, "here_is_key", 5000)
    node_database = download_node_database(session)
    logout_and_close(session)
    print(node_database)

def client4():
    with requests.Session() as session:
        data = {
            "username": username,
            "password": password
        }
    
        response = session.post(login_url, json=data)
        if response.status_code != 200:
            if create_account:
                registration_data = data.copy()
                registration_data["invitation_code"] = "basic_invite"
                response = session.post(register_url, json=registration_data)
                if response.status_code != 200:
                    print("Registration failed")
                    exit(1)
                _ = session.post(login_url, json=data)
            else:
                print("Login failed")
                exit(1)

        api_key = input("API Key: ")
        response = session.post(activate_api_key_url, json={"api_key": api_key})
        print(response.json())

def client3():
    with requests.Session() as session:
        data = {
            "username": username,
            "password": password
        }
    
        response = session.post(login_url, json=data)
        if response.status_code != 200:
            if create_account:
                registration_data = data.copy()
                registration_data["invitation_code"] = "basic_invite"
                response = session.post(register_url, json=registration_data)
                if response.status_code != 200:
                    print("Registration failed")
                    exit(1)
                _ = session.post(login_url, json=data)
            else:
                print("Login failed")
                exit(1)

        response = session.post(request_api_key_url, json={"license_name": "standard_license"})
        api_key = response.json().get("api_key", None)
        print(response.json())

        response = session.post(request_api_key_url, json={"license_name": "standard_license"})
        api_key_2 = response.json().get("api_key", None)
        print(api_key_2, response.json())


def client2():
    with requests.Session() as session:
        data = {
            "username": username,
            "password": password
        }
    
        response = session.post(login_url, json=data)
        if response.status_code != 200:
            if create_account:
                registration_data = data.copy()
                registration_data["invitation_code"] = "basic_invite"
                response = session.post(register_url, json=registration_data)
                if response.status_code != 200:
                    print("Registration failed")
                    exit(1)
                _ = session.post(login_url, json=data)
            else:
                print("Login failed")
                exit(1)

        response = session.post(add_user_license_url, json={"license_name": "special_license"})
        print(response.json())

        response = session.post(request_api_key_url, json={"license_name": "special_license"})
        api_key = response.json().get("api_key", None)
        print(response.json())

        response = session.post(activate_api_key_url, json={"api_key": api_key})
        print(response.json())


def client1():
    with requests.Session() as session:
        data = {
            "username": username,
            "password": password
        }

        print("Attempting Log In")
        response = session.post(login_url, json=data)
        print(response.json())

        if username != "admin":
            time.sleep(1)
            if (response.status_code != 200) and create_account:
                print("Login failed, will try to register account")
                registration_data = data.copy()
                registration_data["invitation_code"] = input("Invitation Code: ")

                print("Attempting Registration")
                response = session.post(register_url, json=registration_data)
                print(response.json())
                if response.status_code != 200:
                    print("Registration failed")
                    exit(1)
                
                time.sleep(1)
                print("Attempting Log In Again")
                response = session.post(login_url, json=data)
                print(response.json())

            
            time.sleep(1)
            print("Getting Home")
            response = session.get(home_url)
            print(response.json())

            time.sleep(1)
            print("Getting Server Status")
            response = session.get(server_status_url)
            print(response.json())

            _ = input("Enter any key: ")

            time.sleep(1)
            print("Logging Out")
            response = session.get(logout_url)
            print(response.json())

            time.sleep(1)
            print("Getting Home After Logout")
            response = session.get(home_url)
            print(response.json())

            _ = input("Enter any key: ").lower()

        else:
            check_again = 'y'
            while check_again == 'y':
                print("Server status")
                response = session.get(server_status_url)
                print(json.dumps(response.json(), indent=2, sort_keys=True))
                check_again = input("Check again? (y/n): ").lower()

if __name__ == "__main__":
    create_account = input("Create account if none exists? (y/n): ").lower() == "y"
    username = input("Username: ")
    password = input("Password: ")
    client_number = int(input("Client number (1-5): "))

    if client_number == 1:
        client1()
    elif client_number == 2:
        client2()
    elif client_number == 3:
        client3()
    elif client_number == 4:
        client4()
    elif client_number == 5:
        client5()