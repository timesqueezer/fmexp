#!/usr/bin/env bash

psql -U postgres -c "DROP DATABASE ${1:-fmexp};"
psql -U postgres -c "CREATE DATABASE ${1:-fmexp};"

FLASK_APP=fmexp env/bin/flask create-tables
