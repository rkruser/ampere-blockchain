import requests
import time
import json

base_url = "https://ryenandvivekstartup.online"
login_url = base_url + "/login"
home_url = base_url + "/home"
logout_url = base_url + "/logout"
register_url = base_url + "/register"
server_status_url = base_url + "/server_status"

create_account = input("Create account if none exists? (y/n): ").lower() == "y"
username = input("Username: ")
password = input("Password: ")

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