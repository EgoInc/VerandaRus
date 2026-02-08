#!/bin/sh
set -e

# Future: collectstatic, DB wait, etc.
python manage.py check || true

exec "$@"
