#!/usr/bin/env bash

set -e

psql -U postgres -c "DROP DATABASE ${2:-fmexp};"
psql -U postgres -c "CREATE DATABASE ${2:-fmexp};"

ssh rho pg_dump -U postgres -Fc ${1:-fmexp-layout1} | pv | pg_restore -U postgres -n public -1 -d ${2:-fmexp}

FLASK_APP=fmexp env/bin/flask db upgrade
