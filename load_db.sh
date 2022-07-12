#!/usr/bin/env bash
set -e

psql -U postgres -c "DROP DATABASE \"${2:-fmexp}\";"
psql -U postgres -c "CREATE DATABASE \"${2:-fmexp}\";"

cat $1 | pxz -d -c - | pv | pg_restore -U postgres -n public -1 -d ${2:-fmexp}
