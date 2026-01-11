#!/bin/bash
# run_beat.sh
echo "Starting Celery beat scheduler..."
# The -A option specifies the Celery application instance.
# The -l info option sets the log level to info.
# The --scheduler option specifies the scheduler to use.
export PYTHONPATH="../..:$PYTHONPATH"
../../.venv/bin/celery -A app.celery_app beat -l info
