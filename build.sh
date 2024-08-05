#!/bin/bash
set -o errexit
set -o pipefail
export FLASK_APP=myapp
export FLASK_ENV=production
export FLASK_DEBUG=True
echo "Starting the application..."
python3 run.py
