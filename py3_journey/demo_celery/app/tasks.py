#!/usr/bin/env python
# coding=utf-8
import logging
import time
from math import sqrt

from py3_journey.demo_celery.app.celery_app import app


# a more advanced logger
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('logs/tasks.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - [%(threadName)s] - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


task_logger = get_logger('celery.tasks')


@app.task
def add(x, y):
    time.sleep(50)
    task_logger.info(f"Adding {x} and {y}")
    return x + y


@app.task
def sqrt_task(value):
    task_logger.info(f"Calculating square root of {value}")
    return sqrt(value)

@app.task(bind=True)
def bind_task(self, i):
    task_logger.info(f'i : {i} , self.request : {self.request}')
    time.sleep(10)

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def failing_task(self):
    try:
        task_logger.info(f"This task will fail and retry, self.request : {self.request}")
        raise ValueError("Intentional error")
    except ValueError as exc:
        task_logger.warning(f"Task failed. Retrying in {self.default_retry_delay} seconds...")
        raise self.retry(exc=exc)


@app.task
def periodic_task():
    task_logger.info("This is a periodic task running every 30 seconds.")
    return "OK"

@app.task
def no_ack_task():
    task_logger.info("This task will not be acknowledged.")
    time.sleep(30)
    task_logger.info("No acknowledgment task completed successfully.")
    return "No acknowledgment"

@app.task(acks_late=True)
def ack_task():
    task_logger.info("This task demonstrates the acknowledgment mechanism.")
    time.sleep(30)
    task_logger.info("Ack task completed successfully.")
    return "Acknowledged"


@app.task(ignore_result=True)
def log_message(message):
    """
    This is a "fire-and-forget" task. Even if a backend is configured,
    Celery will not store the result for this task.
    """
    task_logger.info(f"Logging a message: {message}")
    # No meaningful return value needed

