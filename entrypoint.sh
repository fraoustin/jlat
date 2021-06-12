#!/bin/sh
set -e

if [ "$1" = 'jlat' ]; then
    python -u /jlat/jlat.py
    exit
fi

exec "$@"