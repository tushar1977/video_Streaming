#!/usr/bin/env bash

set -o errexit
export FLASK_APP=myapp

flask db init

flask db migrate
flask db upgrade

python run.py
