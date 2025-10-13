#!/bin/bash
# startup.sh
# exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 backend:backend
# echo $PATH
# ls $LAMBDA_TASK_ROOT
# PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$LAMBDA_TASK_ROOT which gunicorn
# PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$LAMBDA_TASK_ROOT which python
export RUST_BACKTRACE=1
PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$PYTHONPATH:/opt/python:$LAMBDA_RUNTIME_DIR exec python -m gunicorn backend:backend --bind 0.0.0.0:${PORT:-3459} --workers 1 --threads 8
# PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$PYTHONPATH:/opt/python:$LAMBDA_RUNTIME_DIR exec python -c 'print("Hello World!")'
# echo $LAMBDA_TASK_ROOT
# echo $PYTHONPATH
# echo $LAMBDA_RUNTIME_DIR
# echo "It's updating"
# echo "Should get here"
# python -c 'print("Hello World!")'
# python -c 'import pkgutil; for finder, name, ispkg in pkgutil.iter_modules(): print(f"{name:40} {"<pkg>" if ispkg else "<mod>"}")'
# echo "I don't think it's going to get here though"
# python -c 'print("Lovely day, isnt it?")'
# ls
# python test.py
# python -c 'print("Goodbye, World!")'
# echo "Florb"
# exec python -m gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 8 backend:backend
