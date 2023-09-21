import pyaudio
import wave
import math
import struct
import io
import os

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENT_THRESHOLD = 0.01
RECORD_SECONDS = 600

class Recorder:
    def __init__(self):
        self.recording_done_callback = None

    def get_rms(self, data):
        count = len(data)/2
        _format = "%dh" % (count)
        shorts = struct.unpack(_format, data)
        sum_squares = 0.0
        for sample in shorts:
            n = sample * (1.0/32768)
            sum_squares += n*n
        return math.sqrt(sum_squares / count)

    def record(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, input_device_index=int(os.environ.get("AUDIO_DEVICE_INDEX")),
                            frames_per_buffer=CHUNK)

        print("Recording started...")

        frames = []

        silence = 0
        silence_frames = []
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
            rms = self.get_rms(data)
            if rms < SILENT_THRESHOLD:
                silence += 1
                silence_frames.append(data)
            else:
                silence = 0
                silence_frames = []
            if silence > int(RATE / CHUNK * 2):
                break

        print("Recording stopped.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        audio_stream = io.BytesIO()
        wf = wave.open(audio_stream, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

        if self.recording_done_callback is not None:
            self.recording_done_callback(audio_stream)
