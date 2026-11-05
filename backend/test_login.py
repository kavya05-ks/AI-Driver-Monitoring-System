import requests

# ---------------------------
# 1. REGISTER DRIVER
# ---------------------------
register_url = "http://127.0.0.1:5000/register"

register_data = {
    "username": "driver1",
    "password": "12345",
    "role": "driver"
}

register_response = requests.post(register_url, json=register_data)

print("REGISTER")
print(register_response.status_code)
print(register_response.json())


# ---------------------------
# 2. LOGIN DRIVER
# ---------------------------
login_url = "http://127.0.0.1:5000/login"

login_data = {
    "username": "driver1",
    "password": "12345"
}

login_response = requests.post(login_url, json=login_data)

print("\nLOGIN")
print(login_response.status_code)
print(login_response.json())