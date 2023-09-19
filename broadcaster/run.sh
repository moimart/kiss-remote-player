#/bin/bash
# script to run from console
gunicorn broadcaster:app -b 0.0.0.0:8008
