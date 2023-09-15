#/bin/bash
# script to run from console
gunicorn player:app -b 0.0.0.0:8000
