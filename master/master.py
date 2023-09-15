import socket
from flask import Flask, request, jsonify
from zeroconf import ServiceBrowser, Zeroconf
import requests
import threading

app = Flask(__name__)

class ServiceListener:
    def __init__(self):
        self.services = {}

    def remove_service(self, zeroconf, type, name):
        if name in self.services:
            del self.services[name]

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print(f"Found service: {info}")
        address = socket.inet_ntoa(info.address)
        self.services[name] = {
            "address": address,
            "port": info.port
        }


def start_zeroconf_discovery():
    zeroconf = Zeroconf()
    listener = ServiceListener()
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    return zeroconf, listener, browser

zeroconf, listener, browser = start_zeroconf_discovery()

@app.before_first_request
def init_zeroconf_browser():
    ServiceBrowser(zeroconf, "RemotePlayerService._http._tcp.local.", listener)

@app.route('/play', methods=['POST'])
def play():
    data = request.json
    responses = []

    for name, service in listener.services.items():
        url = f"http://{service['address']}:{service['port']}/play"
        try:
            response = requests.post(url, json=data)
            responses.append({
                "service": name,
                "status": response.status_code,
                "response": response.json()
            })
        except requests.RequestException as e:
            responses.append({
                "service": name,
                "error": str(e)
            })

    return jsonify(responses)

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        zeroconf.close()
