import socket
from flask import Flask, request, jsonify
import requests
import threading
import time
from gpthass import GPTHass
import os
from dotenv import load_dotenv
import openai
import whisper
import base64
import numpy as np
import resampy
import wave
import io

load_dotenv()

config = {
    "user_name": os.getenv("HASS_USER_NAME"),
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "hass_host": os.getenv("HASS_HOST"),
    "hass_token": os.getenv("HASS_TOKEN"),
    "broadcaster_ip": os.getenv("BROADCASTER_IP"),
    "broadcaster_port": os.getenv("BROADCASTER_PORT")
}

whisper_model = whisper.load_model("base")

app = Flask(__name__)
gpthass = GPTHass(config=config)
        
def respond_to_request(name, service, data):
    url = f"http://{service['address']}:{service['port']}/play"
    print(f"Sending request to {url}")
    try:
        requests.post(url, json=data)
    except requests.RequestException as e:
        print(f"Error for service {name}: {e}")
 

def audio_to_waveform(binary_data):
    # Use an in-memory bytes buffer
    buf = io.BytesIO(binary_data)
    
    # Open the audio file from the in-memory buffer
    with wave.open(buf, 'rb') as w:
        n_channels, samp_width, framerate, n_frames = w.getparams()[:4]
        audio_binary_data = w.readframes(n_frames)
    
    # Convert audio binary data to a numpy array
    if samp_width == 1:  # 1 byte samples are uint8
        dtype = np.uint8
    elif samp_width == 2:  # 2 byte samples are int16
        dtype = np.int16
    else:
        raise ValueError("Unsupported sample width.")
    
    audio_array = np.frombuffer(audio_binary_data, dtype=dtype)
    
    # If stereo, take the average to convert to mono
    if n_channels == 2:
        audio_array = (audio_array[::2] + audio_array[1::2]) / 2

    # Resample to 16kHz if necessary
    if framerate != 16000:
        audio_array = resampy.resample(audio_array.astype(float), framerate, 16000)
    
    # Convert the float array back to int16
    audio_array = audio_array.astype(np.float32) / 32768.0

    return audio_array      
        
def transcribe(audio_data,name):
    transcription = whisper_model.transcribe(audio_to_waveform(audio_data))
    transcription = transcription["text"].strip()
    play(transcription,name)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    if 'name' not in data:
        return 'No name in the request', 400
    
    if not data or 'audio' not in data:
        return jsonify({"message": "Invalid payload"}), 400

    audio_data = base64.b64decode(data['audio'])
    
    with open("audio.wav", "wb") as f:
        f.write(audio_data)

    if audio_data:
        thread = threading.Thread(target=transcribe, args=(audio_data,data['name']))
        thread.start()
    
    return jsonify({"message": "OK"})
    
def play(answer,name):
    answer = gpthass.answer(answer)
    
    payload = { "text": answer, "name" : name }
    response = requests.post(f'http://{config["broadcaster_ip"]}:{config["broadcaster_port"]}/play', json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4444)
