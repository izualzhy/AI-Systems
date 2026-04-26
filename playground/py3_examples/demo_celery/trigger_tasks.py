#!/usr/bin/env python
# coding=utf-8
import logging
from celery import chain
import sys
sys.path.append('.')
from app.tasks import add, sqrt_task, failing_task, ack_task, log_message, bind_task, no_ack_task

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def run_simple_task():
    logger.info("Dispatching simple 'add' task...")
    # using delay to trigger a task
    result = add.delay(4, 4)
    logger.info(f"Task dispatched. Task ID: {result.id}. Waiting for result...")
    logger.info(f"Result: {result.get(timeout=60)}")

def run_many_simple_tasks():
    for i in range(10):
        logger.info(f"Dispatching simple 'add' task with i={i}...")
        add.delay(i, i)

def run_task_chain():
    logger.info("Dispatching a chain of tasks: sqrt(add(2, 2))...")
    # A chain of tasks is a set of tasks that are executed one after another.
    # The output of the first task is passed as input to the second task.
    c = chain(add.s(2, 2), sqrt_task.s())
    result = c()
    logger.info(f"Task chain dispatched. Waiting for result...")
    logger.info(f"Result: {result.get(timeout=10)}")

def run_bind_task():
    for i in range(1, 4):
        logger.info(f"Dispatching bind_task with i={i}...")
        bind_task.delay(i)

def run_failing_task():
    logger.info("Dispatching a task that is expected to fail and retry...")
    result = failing_task.delay()
    logger.info(f"Task dispatched. Task ID: {result.id}.")
    logger.info("Check the worker logs to see the retry mechanism in action.")
    try:
        # this will raise the exception that caused the task to fail
        result.get()
    except Exception as e:
        logger.error(f"Task failed after retries: {e}")


def run_ack_task():
    logger.info("Dispatching 'ack_task' to demonstrate the acknowledgment mechanism...")
    result_no_ack = no_ack_task.delay()
    result_ack = ack_task.delay()
    logger.info(f"Task dispatched. ack Task ID: {result_ack.id}. no ack TASK ID: {result_no_ack.id}")
    logger.info("You can now stop the worker to see the task get re-queued.")
    # In a real scenario, you wouldn't wait here, but for the demo,
    # we'll wait for the result to show it completes.
    try:
        logger.info(f"Ack Result: {result_ack.get(timeout=100)}")
    except Exception as e:
        logger.error(f"Ack task failed: {e}")
    try:
        logger.info(f"No ack Result: {no_ack_task.get(timeout=100)}")
    except Exception as e:
        logger.error(f"No ack task failed: {e}")


def run_fire_and_forget_task():
    logger.info("Dispatching 'log_message' task (fire-and-forget)...")
    log_message.delay("This task runs without needing a backend.")
    logger.info("Task dispatched. Check worker logs for the output.")


if __name__ == '__main__':
    logger.info("Running Celery task examples...")
    input("Press Enter to continue...")

    # Example 1: Simple task execution
    # run_simple_task()
    # input("Press Enter to continue...")

    run_many_simple_tasks()
    input("Press Enter to continue...")

    # Example 2: A chain of tasks
    run_task_chain()
    input("Press Enter to continue...")

    run_bind_task()
    input("Press Enter to continue...")

    # Example 3: A task that fails and retries
    # Note: The periodic task is scheduled in celery_app.py and will run automatically
    # when celery beat is running.
    run_failing_task()
    input("Press Enter to continue...")

    # Example 4: A task demonstrating acknowledgment
    run_ack_task()
    input("Press Enter to continue...")

    # Example 5: A fire-and-forget task
    run_fire_and_forget_task()

    logger.info("Periodic tasks are running in the background if you have `celery beat` active.")
    logger.info("Check `logs/tasks.log` for output from all tasks.")
