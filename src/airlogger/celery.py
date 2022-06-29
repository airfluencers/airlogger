from datetime import timedelta
import logging
import sys
from time import time
import traceback as tb
from typing import Any
from celery import Celery
from celery.worker.request import Context
from celery.worker.consumer import Consumer
from celery.app.task import Task
from celery.signals import task_success, task_failure, task_internal_error, task_retry, task_received, task_rejected, task_revoked, task_unknown, task_prerun

# Replaces requests module for airlogger.requests module
try:
    # imports requests for forcing original module's register
    import requests

    # import airlogger.requests as airlogger_requests
    from airlogger import requests as airlogger_requests

    # removes original module's register
    del sys.modules['requests']

    # register airlogger as requests
    sys.modules['requests'] = airlogger_requests
except ImportError:
    pass


from airlogger import globals, handler
task_times = {}


def init_app(app: Celery, require_trace_id: bool = False):
    globals.airlogger = logging.getLogger('airlogger')
    globals.airlogger.propagate = True
    globals.airlogger.setLevel(logging.INFO)
    globals.airlogger.addHandler(handler.AirTraceHandler(
        app.namespace, 'webserver', require_trace_id))


def log_signal(
    signal_type,
    task: Task,
    result: Any = None,
    error: str = None,
    traceback=None,
):
    if result:
        try:
            dict_result = dict(result)
            result = dict_result
        except TypeError:
            ...
        except ValueError:
            ...

    request: Context = task.request

    request_id = request.id
    task_name = task.name

    max_retries = task.max_retries
    args = request.args
    hostname = request.hostname
    retries = request.retries

    time_start = None
    time_end = None
    time_elapsed = -1
    try:
        time_start: time = task_times.pop(request_id)
        time_end = time()
        time_elapsed = time_end - time_start
    except KeyError:
        ...

    meta = {
        "signal_type": signal_type,
        "request_id": request_id,
        "task_name": task_name,
        "time_start": time_start,
        "time_end": time_end,
        "time_elapsed": time_elapsed,
        "result": result,
        "error": error,
        "retries": retries,
        "max_retries": max_retries,
        "args": args,
        "hostname": hostname,
    }

    if traceback:
        meta['traceback'] = tb.format_tb(traceback)

    globals.airlogger.info(f'celery tast {signal_type}', meta)


def task_prerun_signal(sender: Task, *args, **kwargs):
    request: Context = sender.request
    task_id = request.id
    task_times[task_id] = time()


def task_success_signal(sender: Task = None, result=None, *args, **kwargs):

    signal_type = "task_success"
    result: Any = result

    log_signal(
        signal_type=signal_type,
        task=sender,
        result=result,
    )
    # Dispatched when a task succeeds.
    ...


def task_failure_signal(sender: Task = None, task_id=None, exception=None, traceback=None, einfo=None, *args, **kwargs):
    # Dispatched when a task fails.

    log_signal(
        signal_type='task_failure',
        task=sender,
        traceback=traceback
    )


def task_internal_error_signal(sender: Task = None, task_id=None, request=None, exception=None, traceback=None, einfo=None, *args, **kwargs):
    # Dispatched when an internal Celery error occurs while executing the task.
    log_signal(
        signal_type='task_internal_error',
        task=sender,
        traceback=traceback
    )


def task_retry_signal(sender: Task = None, request=None, reason: str = None, einfo=None, *args, **kwargs):
    # Dispatched when a task will be retried.

    log_signal(
        signal_type='task_retry',
        task=sender,
        error=str(reason),
    )


def task_received_signal(sender: Consumer = None, request: Context = None, *args, **kwargs):
    # Dispatched when a task is received from the broker and is ready for execution.
    ...


def task_rejected_signal(sender: Consumer = None, message: str = None, exc: Exception = None, *args, **kwargs):
    # Dispatched when a worker receives an unknown type of message to one of its task queues.
    ...


def task_revoked_signal(sender: Consumer = None, request: Context = None, terminated: bool = False, signum: int = None, expired: bool = False, *args, **kwargs):
    # Dispatched when a task is revoked/terminated by the worker.
    ...


def task_unknown_signal(sender: Consumer = None, name: str = None, id: str = None, message: str = None, exc: Exception = None, *args, **kwargs):
    # Dispatched when a worker receives a message for a task that’s not registered.
    ...


def init_signals(*args, **kwargs):
    task_prerun.connect(task_prerun_signal)
    task_success.connect(task_success_signal)
    task_failure.connect(task_failure_signal)
    task_internal_error.connect(task_internal_error_signal)
    task_retry.connect(task_retry_signal)
    task_received.connect(task_received_signal)
    task_rejected.connect(task_rejected_signal)
    task_revoked.connect(task_revoked_signal)
    task_unknown.connect(task_unknown_signal)
