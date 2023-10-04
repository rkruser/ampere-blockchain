import requests
import time
import json

base_url = "https://ryenandvivekstartup.online"
login_url = base_url + "/login"
home_url = base_url + "/home"
logout_url = base_url + "/logout"
register_url = base_url + "/register"
server_status_url = base_url + "/server_status"
add_user_license_url = base_url + "/add_user_license"
request_api_key_url = base_url + "/request_api_key"
activate_api_key_url = base_url + "/activate_api_key"

create_account = input("Create account if none exists? (y/n): ").lower() == "y"
username = input("Username: ")
password = input("Password: ")
client_number = int(input("Client number (1-4): "))


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

if client_number == 1:
    client1()
elif client_number == 2:
    client2()
elif client_number == 3:
    client3()
elif client_number == 4:
    client4()