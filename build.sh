#!/usr/bin/env bash

set -o errexit
export FLASK_APP=myapp
export FLASK_DEBUG=False
if [ ! -f "/app/db_initialized" ]; then
	echo "Initializing database..."
	flask db init
	touch /app/db_initialized
else
	echo "Database already initialized, skipping initialization."
fi

echo "Running database migrations..."
flask db migrate
flask db upgrade

echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 4 "run:app"
