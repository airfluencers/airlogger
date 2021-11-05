import json
import logging
import sys
import time
from types import FunctionType
from uuid import uuid4

from airlogger import globals
from airlogger.exceptions import AirTraceIdRequired, InvalidHookResult
from airlogger.handler import AirTraceHandler

try:
    import requests
    sys.modules['requests'] = requests
except ImportError:
    pass


def init_app(app, require_trace_id: bool = True):
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    from fastapi.responses import JSONResponse
    
    globals.airlogger = logging.getLogger('airlogger')
    globals.airlogger.propagate = True
    globals.airlogger.setLevel(logging.INFO)
    globals.airlogger.addHandler(AirTraceHandler(app.title, 'webserver', require_trace_id))

    async def receive_body(request: Request):

        # workaround to get body

        receive_ = await request._receive()

        async def receive():
            return receive_

        request._receive = receive

    async def func(request: Request, call_next):

        globals.air_trace_id = request.headers.get('X-Air-Trace-Id')
        start_time = time.time()

        await receive_body(request)
        body = await request.body()
        body = body.decode()

        try:
            body = json.loads(body)
        except ValueError:
            pass

        air_request_id = str(uuid4())

        meta = {
            'method': request.method,
            'endpoint': request.url.path,
            'request_id': air_request_id,
            'event_type': 'REQUEST',
            'body': body,
        }

        if isinstance(app.extra.get('AIR_HOOK_LOG_REQUEST'), FunctionType):
            hook_result = app.extra.get['AIR_HOOK_LOG_REQUEST'](request)
            if not type(hook_result) == dict:
                raise InvalidHookResult
            meta.update(hook_result)
        try:
            globals.airlogger.info('incoming request', meta)
        except AirTraceIdRequired as e:
            return JSONResponse(status_code=400, content={'msg': e.http_response})

        response = await call_next(request)
        process_time = time.time() - start_time

        meta = {
            'event_type': 'RESPONSE',
            'endpoint': request.url.path,
            'response_time': process_time,
            'request_id': air_request_id
        }

        if isinstance(app.extra.get('AIR_HOOK_LOG_RESPONSE'), FunctionType):
            hook_response = app.extra.get['AIR_HOOK_LOG_RESPONSE'](response)
            if not type(hook_response) == dict:
                raise InvalidHookResult
            meta.update(hook_response)

        globals.airlogger.info('outcoming request', meta)

        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=func)

    return app
