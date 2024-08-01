#!/bin/bash
set -o errexit
set -o pipefail
export FLASK_APP=myapp
export FLASK_ENV=production
export FLASK_DEBUG=False
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --threads 4 "run:app"
