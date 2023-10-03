import requests

url = "https://ryenandvivekstartup.online/login"

# Disable warnings for self-signed certificates. Do NOT do this in production.
#requests.packages.urllib3.disable_warnings()

data = {
    "username": "user2",
    "password": "password2234"
}

response = requests.post(url, json=data)
print(response.json()['message'])
