FROM arm32v7/python:3.10.9-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 8008

COPY . .

CMD ["gunicorn", "server:app", "-b", "0.0.0.0:4444"]
