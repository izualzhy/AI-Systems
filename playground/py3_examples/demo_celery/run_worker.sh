#!/bin/bash
# run_worker.sh
# Generate a random number for the worker name
RANDOM_ID=$$
WORKER_NAME="worker_${RANDOM_ID}@%h"
echo "Starting Celery worker with name: $WORKER_NAME"
# The -A option specifies the Celery application instance.
# The -l info option sets the log level to info.
# The -P solo option is used for local development, it runs the worker in a single process.
# Remove -P solo for production environments to use multiple processes.
export PYTHONPATH="../..:$PYTHONPATH"
../../.venv/bin/celery -A app.celery_app worker -l info -P threads -Q default,periodic_tasks -c 1 -n $WORKER_NAME