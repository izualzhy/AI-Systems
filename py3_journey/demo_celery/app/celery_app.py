#!/usr/bin/env python
# coding=utf-8

from celery import Celery
from kombu import Queue, Exchange

app = Celery('demo_celery',
             broker='redis://localhost/0',
             backend='redis://localhost/0',
             include=['app.tasks'])

app.conf.update(
    result_expires=3600,
    task_queues=(
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('periodic_tasks', Exchange('periodic_tasks'), routing_key='periodic_tasks'),
    ),
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
)

app.conf.beat_schedule = {
    'periodic_task-every-30-seconds': {
        'task': 'app.tasks.periodic_task',
        'schedule': 120.0,
        'options': {'queue': 'periodic_tasks'}
    },
}
