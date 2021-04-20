from airlogger.exceptions import AirTraceIdRequired, InvalidArgsType
from logging import StreamHandler
import logging
import os
import json
from airlogger import globals
import sys
import datetime
import traceback


# sys.modules["requests"] = lambda x: print(x)

class AirTraceHandler(StreamHandler):
    def __init__(self, service_name: str, service_type: str, require_trace_id: bool = True) -> None:
        self.service_name = service_name
        self.service_type = service_type
        self.require_trace_id = require_trace_id
        super().__init__(stream=sys.stdout)
    
    def verify_trace_id(self):
        if self.require_trace_id and not globals.air_trace_id:
            raise AirTraceIdRequired

    def emit(self, record):
        self.verify_trace_id()
        if record.args and type(record.args) != dict:
            raise InvalidArgsType
        
        log_record = {
            'hostname': os.environ.get('HOSTNAME'),
            'level': record.levelname,
            'timetsamp': datetime.datetime.now().timestamp(),
            'msg': record.msg,
            'app_name': self.service_name,
            'app_type': self.service_type,
            'air_trace_id': globals.air_trace_id,
            'msg': record.msg,
            'traceback': str(traceback.print_exc()) if record.levelno >= logging.ERROR else None,
            'meta': record.args
        }
        
        self.stream.write(json.dumps(log_record) + '\n')