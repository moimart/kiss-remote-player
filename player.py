from flask import Flask, request, jsonify
import hashlib
import os
import requests
import pygame
import socket
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
MP3_FOLDER = os.getenv("MP3_FOLDER")
SERVICE_URL = os.getenv("SERVICE_URL")
VOICE_ID = os.getenv("VOICE_ID")
API_KEY = os.getenv("API_KEY")
MASTER_IP = os.getenv("MASTER_IP")
MASTER_PORT = os.getenv("MASTER_PORT")
HOST_IP = socket.gethostname() if os.getenv("HOST_IP") is None else os.getenv("HOST_IP")

if not os.path.exists(MP3_FOLDER):
    os.makedirs(MP3_FOLDER)

def sha256_string(input_str):
    return hashlib.sha256(input_str.encode('utf-8')).hexdigest()

@app.route('/play', methods=['POST'])
def post_endpoint():
    data = request.get_json()
    input_string = data.get('text', '')

    if not input_string:
        return jsonify({'error': 'text not provided'}), 400

    hashed_filename = sha256_string(input_string) + ".mp3"
    full_path = os.path.join(MP3_FOLDER, hashed_filename)

    if os.path.exists(full_path):
        pygame.mixer.init()
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        return jsonify({'message': 'Audio played'}), 200

    payload = \
    {
        "text": input_string,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": \
        {
            "stability": 1,
            "similarity_boost": 1,
            "style": 0,
            "use_speaker_boost": True
        }
    }
    
    headers = \
    {
        'Content-Type': 'application/json',
        'xi-api-key': API_KEY
    }
    
    url = f"{SERVICE_URL}/v1/text-to-speech/{VOICE_ID}"
    
    print(url)

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        with open(full_path, 'wb') as f:
            f.write(response.content)
        
        pygame.mixer.init()
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        return jsonify({'message': 'Audio retrieved, saved and played'}), 200
    else:
        # Log the error
        with open("error.log", "a") as f:
            f.write(f"Error with status code {response.status_code}: {response.text}\n")
        return jsonify({'error': 'Service failed'}), 500

@app.route('/discover', methods=['GET'])
def discover():
    return jsonify({"message": "Remote Player Service is up!"})

def register_to_master():
    url = f"http://{MASTER_IP}:{MASTER_PORT}/register"
    print(url)
    
    try:
        response = requests.post(url, json={
            "name": "player" + socket.gethostname(),
            "service": "player",
            "address": socket.gethostbyname(HOST_IP),
            "port": 8000
        })

        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

        print("Registered to master")

    except requests.RequestException:
        print("Failed to register to master.")

def periodic_register():
    while True:
        register_to_master()
        time.sleep(300)  # sleep for 5 minutes (300 seconds)

print("trying to register to master")

# Start the periodic registration in a separate thread
thread = threading.Thread(target=periodic_register)
thread.start()

if __name__ == "__main__":
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=8000)






