import requests

response = requests.get("https://api.ipify.org?format=json")
ip = response.json()["ip"]
print(f"Outbound IP: {ip}")
