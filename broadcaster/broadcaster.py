import socket
from flask import Flask, request, jsonify
import requests
import threading
import time

services = {}

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
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
        # You can log the error if you want
        print(f"Error for service {name}: {e}")

@app.route('/play', methods=['POST'])
def play():
    data = request.json

    if 'name' in data and data['name'] in services:
        threading.Thread(target=make_request, args=(data['name'], services[data['name']], data)).start()
    else:
        for name, service in services.items(): 
            threading.Thread(target=make_request, args=(name, service, data)).start()


    return jsonify({"message": "Requests are being processed in the background."})

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
