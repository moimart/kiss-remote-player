# write the docker file to run this python 3.10.9 app with gunicorn player:app

FROM arm32v7/python:3.10.9-buster

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN apt-get update && apt-get install ffmpeg portaudio19-dev libsmpeg0 pulseaudio alsa-utils libasound2 libasound2-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev -y
RUN pip3 install -r requirements.txt
RUN pip3 install pyaudio


COPY . .

CMD ["python", "assistant.py"]
