#!/usr/bin/env bash

# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

export FLASK_APP=myapp
# Run migrations
flask db init
flask db migrate
flask db upgrade
