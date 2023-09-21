#/bin/bash
# script to run from console
gunicorn assistant:app -b 0.0.0.0:5555
