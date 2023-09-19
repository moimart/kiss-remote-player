kiss-remote-player
=====

# What the heck is this?

This a 'keep-it-simple-stupid" home broadcaster for elevenlabs voices

The use case is very simple: 

### *You want to make your favorite AI-voice to announce things at home and you want to do it inexpensively*

It contains two containers to be run on Raspberry Pi Zeros or any arm32v7 board with sound capabilities

I use at home Raspberry Pi Zeros with Anker S330 conf speakers

One container is the 'player' and it provides a simple http endpoint to speak out loud the message on the device.

The other container is the broadcaster and it provides a simple http endpoint to speak out the message on all speakers that register to it. The endpoint also allow to point to a specific 'player'

# Setup

## Player

You need an .env file (you can rename .env.sample to it) add the voice id and you API key from elevenlabs. You might
need to get the voice id querying the elevenlabs API (link to elevenlabs API)

Edit the docker-compose and edit the following environment variables:

- MASTER_IP = 'This must be the IP address of the broadcaster'
- AUDIODEV = 'This must be the alsa hardware address of the device; It defaults to the anker in raspi zero'

in the player device you need to export a environment variable called HOST_IP, like this:

```
$ export HOST_IP=$(hostname -I | awk '{print $1}')
```

Once you have this you can just run docker-compose up -d and the image for the container should be fetched and started.

## Broadcaster

You only need to export a environment variable called HOST_IP, like this:

```
$ export HOST_IP=$(hostname -I | awk '{print $1}')
```

Once you have this you can just run docker-compose up -d and the image for the container should be fetched and started.

You could run the broadcaster and the player on the same device. All players point to a single broadcaster so adding more broadcasters has no real use. 
Unless you want to create groups

# Building

If you want to build the containers, just do a normal docker build in the machine:

```
$ docker build -t player .
```

BUT I DON'T RECOMMEND THIS AS IT WILL BUILD pygame AND IT WILL TAKE TIME ON YOUR BOARD!!!

Instead, use a container registry (like Github's) and edit the build-arm32v7.sh script pointing to your container registry and it will build and upload it there. Then change the docker-compose to use the image from your container registry accordingly.

# How it's working

Every 5 minutes each player registers itself to the broadcaster. There is no authentication whatsoever as it tries to be very simple. If you want to make it more robust, contributions are welcome 🙂. Don't use this in a public network; Use it in your own private network!!! It's not secure.

Every 5 minutes the broadcaster pings each player to know whether they are alive or not

# Usage

just send a *POST* HTTP request to the url of the broadcaster like this: 

http://{IP_ADDRESS}:8008/play 

with a JSON payload as such:

{ "text": "I'm sorry Dave but I'm afraid I can't do that... ... ... ..." }

Optionally, you can add a key called "name" with the string "{HOSTNAME}" (substitute {HOSTNAME} with the real text hostname of the player device) and it would only play on that player.

You can also send the same type of *POST* HTTP request (without the optional "name" key) to the url of the player like this:

http://{IP_ADDRES}:8000/play

