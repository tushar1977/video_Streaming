#!/bin/bash
set -o errexit
set -o pipefail

export FLASK_APP=myapp
export FLASK_ENV=production
export FLASK_DEBUG=False

if [ ! -d "/app/migrations" ]; then
	echo "Initializing database..."
	flask db init || {
		echo "Database initialization failed"
		exit 1
	}
else
	echo "Migrations directory already exists, skipping initialization."
fi

echo "Checking for database migrations..."
if flask db migrate | grep -q "No changes detected"; then
	echo "No new migrations detected."
else
	echo "Running database migrations..."
	flask db migrate || {
		echo "Database migration failed"
		exit 1
	}
	flask db upgrade || {
		echo "Database upgrade failed"
		exit 1
	}
fi

echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 4 "run:app"
