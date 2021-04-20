
from airlogger import globals
import requests

class Session(requests.Session):
    def __init__(self):
        super().__init__()

    def request(self, method, url, *args, **kwargs):

        if kwargs.get('headers'):
            kwargs['headers'].update({
                'X-Air-Trace-Id': globals.air_trace_id,
            })
        else:
            kwargs['headers'] = {'X-Air-Trace-Id': globals.air_trace_id}
        
        return super().request(method, url, *args, **kwargs)

def get(url, *args, **kwargs):
    if kwargs.get('headers'):
        kwargs['headers'].update({
            'X-Air-Trace-Id': globals.air_trace_id,
        })
    else:
        kwargs['headers'] = {'X-Air-Trace-Id': globals.air_trace_id}
    
    return requests.get(url, *args, **kwargs)

def post(url, *args, **kwargs):
    if kwargs.get('headers'):
        kwargs['headers'].update({
            'X-Air-Trace-Id': globals.air_trace_id,
        })
    else:
        kwargs['headers'] = {'X-Air-Trace-Id': globals.air_trace_id}
    
    return requests.post(url, *args, **kwargs)

def put(url, *args, **kwargs):
    if kwargs.get('headers'):
        kwargs['headers'].update({
            'X-Air-Trace-Id': globals.air_trace_id,
        })
    else:
        kwargs['headers'] = {'X-Air-Trace-Id': globals.air_trace_id}
    
    return requests.put(url, *args, **kwargs)

def delete(url, *args, **kwargs):
    if kwargs.get('headers'):
        kwargs['headers'].update({
            'X-Air-Trace-Id': globals.air_trace_id,
        })
    else:
        kwargs['headers'] = {'X-Air-Trace-Id': globals.air_trace_id}
    return requests.delete(url, *args, **kwargs)

def patch(url, *args, **kwargs):
    if kwargs.get('headers'):
        kwargs['headers'].update({
            'X-Air-Trace-Id': globals.air_trace_id,
        })
    else:
        kwargs['headers'] = {'X-Air-Trace-Id': globals.air_trace_id}
    return requests.patch(url, *args, **kwargs)


