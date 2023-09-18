import socket
from flask import Flask, request, jsonify
import requests
import threading

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

    for name, service in services.items():
        # Start a new thread for each request
        threading.Thread(target=make_request, args=(name, service, data)).start()

    return jsonify({"message": "Requests are being processed in the background."})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
