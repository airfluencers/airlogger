import json
import logging
import sys
import time
from types import FunctionType
from uuid import uuid4

from airlogger import globals
from airlogger.exceptions import AirTraceIdRequired, InvalidHookResult
from airlogger.utils.sanitizer import sanitize_body
from starlette.concurrency import iterate_in_threadpool
from airlogger.handler import AirTraceHandler


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

LOG_BLACKLIST = [
    '/docs',
    '/redoc',
    '/openapi.json'
]




def init_app(
    app,
    require_trace_id: bool = True,
    logger_level: str = logging.INFO,
    log_request_body: str = True,
    log_response_body: str = True
):
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.datastructures import UploadFile
    from fastapi.responses import JSONResponse

    globals.airlogger = logging.getLogger('airlogger')
    globals.airlogger.propagate = True

    if logger_level:
        globals.airlogger.setLevel(logger_level)

    globals.airlogger.addHandler(AirTraceHandler(
        app.title, 'webserver', require_trace_id
    ))

    async def receive_body(request: Request):

        # workaround to get body

        receive_ = await request._receive()

        async def receive():
            return receive_

        request._receive = receive

    async def func(request: Request, call_next):

        globals.air_trace_id = request.headers.get(
            'X-Air-Trace-Id', str(uuid4()))
        start_time = time.time()

        await receive_body(request)
        body_content = {}

        form_data = await request.form()
        files = []

        if log_request_body:
            for field in form_data:
                form_field = form_data[field]
                if isinstance(form_field, UploadFile):
                    files.append(form_field)

            if files:
                body_content = {
                    'files': [f.filename for f in files]
                }

            else:
                try:
                    body = await request.body()
                    body = body.decode()
                    body_content = json.loads(body)
                except ValueError:
                    pass
                except UnicodeDecodeError:
                    pass

        air_request_id = str(uuid4())

        meta = {
            'method': request.method,
            'endpoint': request.url.path,
            'request_id': air_request_id,
            'event_type': 'REQUEST',
            'body': sanitize_body(body_content),
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
            'request_id': air_request_id,
            'status_code': response.status_code
        }

        files = []
        body_content = {}

        if log_response_body:
            if request.url.path not in LOG_BLACKLIST:
                try:
                    response_body = [section async for section in response.body_iterator]
                    response.body_iterator = iterate_in_threadpool(
                        iter(response_body))
                    body_content = json.loads(response_body[0].decode())

                except ValueError:
                    pass
                except UnicodeDecodeError:
                    pass

        meta.update({'body': sanitize_body(body_content)})

        if isinstance(app.extra.get('AIR_HOOK_LOG_RESPONSE'), FunctionType):
            hook_response = app.extra.get['AIR_HOOK_LOG_RESPONSE'](response)
            if not type(hook_response) == dict:
                raise InvalidHookResult
            meta.update(hook_response)

        globals.airlogger.info('outcoming request', meta)

        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=func)

    return app
