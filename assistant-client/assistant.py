from porcupine import Porcupine
from recorder import Recorder
from soundboard import SoundBoard
import os
from dotenv import load_dotenv
import base64
import socket
import requests
import threading

load_dotenv()

class AssistantEngine:
    def __init__(self):
        load_dotenv()
        
        self.shared_data = None
        
        self.asr_active = False
        
        self.wake_word_engine = Porcupine(
        keywords=[os.environ.get("PORCUPINE_KEYWORD")] if os.environ.get("PORCUPINE_KEYWORD") != "" else None,
        keyword_paths=[os.environ.get("PORCUPINE_KEYWORD_PATH")] if os.environ.get("PORCUPINE_KEYWORD_PATH") != "" else None,
        access_key=os.environ.get("PORCUPINE_ACCESS_KEY"),
        sensitivities=[0.9],
        input_device_index=os.environ.get("PORCUPINE_INPUT_DEVICE_INDEX")
        )
        
        self.soundboard = SoundBoard()

        self.recorder = Recorder()
        self.recorder.recording_done_callback = self.send_audio_stream
        
        self.wake_word_engine.callback = self.wake_word_detected
        
    def run(self):
        while True:
            self.shared_data = {"state": "idle"}
            self.wake_word_engine.run()
            
    def play_chime(self):
        self.soundboard.play("chime")
        
    def wake_word_detected(self, keyword_index):
        self.shared_data = {"state": "detected"}
        print("wake word detected {}".format(keyword_index))
        self.wake_word_engine.stop()
        self.asr_active = True
        
        thread = threading.Thread(target=self.play_chime)
        thread.start()
        self.shared_data = {"state": "detecting"}
        self.recorder.record()
            
    def send_audio_stream(self, audio_stream):
        encoded_audio = base64.b64encode(audio_stream.getvalue()).decode("utf-8")
        
        url = "http://" + os.environ.get("ASSISTANT_HOST") + "/ask" # http://localhost:5000/asr
        
        payload = {
            "name": socket.gethostname(),
            "audio": encoded_audio
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            print(response.status_code, response.reason)
        except:
            print("Error sending audio stream")
            
if __name__ == "__main__":
    assistant = AssistantEngine()
    assistant.run()