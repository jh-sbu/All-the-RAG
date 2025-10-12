#!/bin/bash
# startup.sh
# exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 backend:backend
echo $PATH
echo $LAMBDA_TASK_ROOT
# ls $LAMBDA_TASK_ROOT
# PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$LAMBDA_TASK_ROOT which gunicorn
# PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$LAMBDA_TASK_ROOT which python
PATH=$PATH:$LAMBDA_TASK_ROOT/bin PYTHONPATH=$LAMBDA_TASK_ROOT exec python -m gunicorn backend:backend --bind 0.0.0.0:${PORT:8080} --workers 1 --threads 8
