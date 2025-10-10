#!/bin/bash
# startup.sh
# exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 backend:backend
echo $PATH
gunicorn backend:backend --bind 0.0.0.0:${PORT:8080} --workers 1 --threads 8
