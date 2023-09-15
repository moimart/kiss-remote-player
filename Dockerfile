# write the docker file to run this python 3.10.9 app with gunicorn player:app

FROM python:3.10.9-buster

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 8000

COPY . .

CMD ["gunicorn", "player:app", "-b", "0.0.0.0:8000"]