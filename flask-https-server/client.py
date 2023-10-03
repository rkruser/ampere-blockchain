import requests

login_url = "https://ryenandvivekstartup.online/login"

# Disable warnings for self-signed certificates. Do NOT do this in production.
#requests.packages.urllib3.disable_warnings()

data = {
    "username": "user1",
    "password": "password1"
}

response = requests.post(login_url, json=data)
print(response.json())

my_session_key = None
if "session_key" in response.json():
    my_session_key = response.json()["session_key"]
    home_url = "https://ryenandvivekstartup.online/home"
    data = {
        "session_key": my_session_key
    }
    response = requests.post(home_url, json=data)
    print(response.json())