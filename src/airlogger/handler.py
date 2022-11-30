from typing import Any, Dict
from airlogger.exceptions import AirTraceIdRequired, InvalidArgsType
from logging import LogRecord, StreamHandler
import logging
import os
import json
from airlogger import globals
import sys
import datetime
import traceback
import ast

# sys.modules["requests"] = lambda x: print(x)


class AirTraceHandler(StreamHandler):
    def __init__(self, service_name: str, service_type: str, require_trace_id: bool = True, use_colors: bool = False) -> None:
        self.service_name = service_name
        self.service_type = service_type
        self.require_trace_id = require_trace_id
        self.use_colors = use_colors
        super().__init__(stream=sys.stdout)

    def verify_trace_id(self):
        if self.require_trace_id and not globals.air_trace_id:
            raise AirTraceIdRequired

    def format_message_as_string(self, message) -> str:

        if isinstance(message, str):
            try:
                return ast.literal_eval(message)
            except Exception:
                ...

        if isinstance(message, dict):
            try:
                return json.dumps(message)
            except Exception:
                ...

        return str(message)

    def format_record(self, record: Dict[str, Any]) -> None:
        str_record = json.dumps(record)
        color_code = 30

        if self.use_colors:
            return f"\033[0;{color_code}m{str_record}\033[0m\n"

        return str_record

    def emit(self, record):
        self.verify_trace_id()
        if record.args and type(record.args) != dict:
            raise InvalidArgsType

        message = self.format_message_as_string(record.msg)

        traceback_exception = traceback.format_exc()
        str_traceback_exception = None

        if 'NoneType' not in traceback_exception and record.levelno >= logging.ERROR:
            str_traceback_exception = str(traceback_exception)

        log_record = {
            'hostname': os.environ.get('HOSTNAME'),
            'level': record.levelname,
            'timetsamp': datetime.datetime.now().timestamp(),
            'msg': message,
            'app_name': self.service_name,
            'app_type': self.service_type,
            'air_trace_id': globals.air_trace_id,
            'traceback': str_traceback_exception,
            'meta': record.args
        }

        str_record = self.format_record(log_record)
        self.stream.write(str_record)

        if record.levelno >= logging.ERROR and 'NoneType' not in traceback.format_exc():
            traceback.print_exc()
