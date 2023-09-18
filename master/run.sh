#/bin/bash
# script to run from console
gunicorn master:app -b 0.0.0.0:8008
