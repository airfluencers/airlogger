
from airlogger import globals
import requests


def _inject_air_trace(kwargs):
    headers = kwargs.get('headers')
    # using "if not" instead .get's default for preventing forced None parameter

    if not isinstance(headers, dict):
        headers = {}

    headers['X-Air-Trace-Id'] = globals.air_trace_id

    kwargs['headers'] = headers
    return kwargs


class Session(requests.Session):
    def __init__(self):
        super().__init__()

    def request(self, method, url, *args, **kwargs):

        _inject_air_trace(kwargs)
        return super().request(method, url, *args, **kwargs)


def get(url, *args, **kwargs):
    _inject_air_trace(kwargs)
    return requests.get(url, *args, **kwargs)


def post(url, *args, **kwargs):
    _inject_air_trace(kwargs)
    return requests.post(url, *args, **kwargs)


def put(url, *args, **kwargs):
    _inject_air_trace(kwargs)
    return requests.put(url, *args, **kwargs)


def delete(url, *args, **kwargs):
    _inject_air_trace(kwargs)
    return requests.delete(url, *args, **kwargs)


def patch(url, *args, **kwargs):
    _inject_air_trace(kwargs)
    return requests.patch(url, *args, **kwargs)
