import socket
from flask import Flask, request, jsonify, abort
import requests
import threading
import time
import os
from dotenv import load_dotenv
import ipaddress

load_dotenv()

services = {}

app = Flask(__name__)

GLOBAL_TOKEN = os.getenv("BROADCASTER_TOKEN")
ALLOWED_NETWORK = ipaddress.ip_network(os.getenv("ALLOWED_NETWORK"))

@app.route('/register', methods=['POST'])
def register():
    client_ip = ipaddress.ip_address(request.remote_addr)
    
    if client_ip not in ALLOWED_NETWORK:
        # Extract the bearer token from the request headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Compare the token to the global variable
            if token != GLOBAL_TOKEN:
                # If the token does not match, abort the request
                abort(401, description="Unauthorized access.")
        else:
            # If there's no bearer token in the headers, abort the request
            abort(401, description="Bearer token is missing.")
            
    data = request.json
    services[data['name']] = {
        "address": data['address'],
        "port": data['port']
    }
    print(f"Registered {data['name']} with address {data['address']}:{data['port']}")
    return jsonify({"message": "registered"})

def make_request(name, service, data):
    url = f"http://{service['address']}:{service['port']}/play"
    try:
        requests.post(url, json=data)
    except requests.RequestException as e:
        print(f"Error for service {name}: {e}")



@app.route('/play', methods=['POST'])
def play():
    client_ip = ipaddress.ip_address(request.remote_addr)
    
    if client_ip not in ALLOWED_NETWORK:
        # Extract the bearer token from the request headers
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Compare the token to the global variable
            if token != GLOBAL_TOKEN:
                # If the token does not match, abort the request
                abort(401, description="Unauthorized access.")
        else:
            # If there's no bearer token in the headers, abort the request
            abort(401, description="Bearer token is missing.")

def periodic_check():
    while True:
        to_delete = []
        for name, service in services.items():
            url = f"http://{service['address']}:{service['port']}/health"
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"Service {name} is not responding. Removing from list.")
                    to_delete.append(name)
            except requests.RequestException:
                print(f"Service {name} is not responding. Removing from list.")
                to_delete.append(name)
                
        for name in to_delete:
            del services[name]        
        
        time.sleep(300)  # sleep for 5 minutes (300 seconds)`

thread = threading.Thread(target=periodic_check)
thread.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
