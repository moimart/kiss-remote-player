import pyaudio
import numpy as np
from openwakeword.model import Model
import argparse
import pyaudio
from threading import Thread

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280

class OpenWakeEngine(Thread):
    
    def __init__(self,model_path,chunk_size,inference_framework,input_device_index):
        Thread.__init__(self)
        self.model = Model(wakeword_models=[model_path],inference_framework=inference_framework)
        self.chunk_size = chunk_size
        self.input_device_index = input_device_index
        self.callback = None

    def stop(self):
        pass
        
    def run(self):
        print("Listening...")
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=self.input_device_index)
        stream.start_stream()
        self.model.reset()
        while True:
            audio_frame = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            prediction = self.model.predict(audio_frame)

            for mdl in self.model.prediction_buffer.keys():

                scores = list(self.model.prediction_buffer[mdl])
                
                if scores[-1] > 0.5:
                    stream.stop_stream()
                    stream.close()
                    
                    self.callback('ok')

                    return
                

