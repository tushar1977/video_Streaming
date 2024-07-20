#!/usr/bin/env bash

set -o errexit
export FLASK_APP=myapp

if [ ! -d "migrations" ]; then
	flask db init
fi

flask db migrate
flask db upgrade

python run.py
