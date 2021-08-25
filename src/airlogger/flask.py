from types import FunctionType
from airlogger.exceptions import AirTraceIdRequired, InvalidHookResult
from airlogger.handler import AirTraceHandler
from airlogger import globals
from uuid import uuid4
import logging
import time
import sys
from airlogger import requests

try:
    import requests
    sys.modules['requests'] = requests
except ImportError:
    pass


def init_app(app, require_trace_id: bool = True):
    from flask import request, g
    
    globals.airlogger = logging.getLogger('airlogger')
    globals.airlogger.propagate = True
    globals.airlogger.setLevel(logging.INFO)
    globals.airlogger.addHandler(AirTraceHandler(app.config.get('APP_NAME', 'AIRLOG'), 'webserver', require_trace_id))

    @app.before_request
    def before_request():
        globals.air_trace_id = request.headers.get('X-Air-Trace-Id')
        g.air_timestamp = time.time()
        g.air_request_id = str(uuid4())

        meta = {
            'method': request.method,
            'endpoint': request.endpoint,
            'request_id': g.air_request_id,
            'event_type': 'REQUEST'
        }
        
        if isinstance(app.config.get('AIR_HOOK_LOG_REQUEST'), FunctionType):
            hook_result = app.config.get['AIR_HOOK_LOG_REQUEST'](request)
            if not type(hook_result) == dict:
                raise InvalidHookResult
            meta.update(hook_result)
        try:
            globals.airlogger.info('incoming request', meta) 
        except AirTraceIdRequired as e:
            return {'msg': e.http_response}, 400  
    
    
    @app.after_request
    def after_request(response):
        meta = {
            'event_type': 'RESPONSE',
            'endpoint': request.endpoint,
            'response_time': int(g.air_timestamp - time.time()),
            'request_id': g.air_request_id,
            'status_code': request.status_code,
        }

        if isinstance(app.config.get('AIR_HOOK_LOG_RESPONSE'), FunctionType):
            hook_response = app.config.get['AIR_HOOK_LOG_RESPONSE'](response)
            if type(hook_response) == dict:
                raise InvalidHookResult
            meta.update(hook_response)

        globals.airlogger.info('outcoming request', meta)
        return response
    
    return app
