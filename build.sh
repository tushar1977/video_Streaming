#!/bin/bash
set -o errexit
set -o pipefail
export FLASK_APP=myapp
export FLASK_ENV=production
export FLASK_DEBUG=True
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} "run:app"
