#/bin/bash
# script to run from console
gunicorn server:app -b 0.0.0.0:4444
