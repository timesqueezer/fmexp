#!/usr/bin/env bash

set -e

pg_dump -U postgres -Fc ${2:-fmexp} | pv | xz -z -T 0 > "$1"
