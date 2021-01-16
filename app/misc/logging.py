import logging
import traceback
from logging import Logger as BaseLogger
from logging.handlers import TimedRotatingFileHandler
from types import MappingProxyType
from typing import Any

import fast_json
from fast_json import convert
from prettylog import JSONLogFormatter as BaseJsonFormatter

from app.config import app_config

__all__ = ['get_logger']
_loggers = {}


@convert.register(object)
def _obj(value):
    return str(value)


class Logger(BaseLogger):
    def _log(
            self,
            level: int,
            msg: Any,
            args,
            exc_info=None,
            extra=None,
            stack_info=False,
            stacklevel=1,
            **kwargs,
    ) -> None:
        extra = extra or {}
        if kwargs:
            extra.update(kwargs)

        return super(Logger, self)._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


class JSONLogFormatter(BaseJsonFormatter):
    def format(self, record: logging.LogRecord):
        record_dict = MappingProxyType(record.__dict__)

        data = dict(errno=0 if not record.exc_info else 255)

        for key, value in self.FIELD_MAPPING.items():
            mapping, field_type = value

            v = record_dict.get(key)

            if not isinstance(v, field_type):
                v = field_type(v)

            data[mapping] = v

        for key in record_dict:
            if key in data or key[0] == "_":
                continue

            value = record_dict[key]

            if value is None:
                continue

            data[key] = value

        for idx, item in enumerate(data.pop('args', [])):
            data['argument_%d' % idx] = str(item)

        payload = {
            'fields': data,
            'msg': record.getMessage(),
            'level': self.LEVELS[record.levelno],
        }

        if isinstance(record.msg, dict):
            data['message_raw'] = ''
            payload['msg'] = record.msg

        if self.datefmt:
            payload['timestamp'] = self.formatTime(record, self.datefmt)

        if record.exc_info:
            payload['stackTrace'] = "\n".join(
                traceback.format_exception(*record.exc_info)
            )

        return fast_json.dumps(payload, ensure_ascii=False)


def get_logger(name: str, level: str = None) -> Logger:
    logger = _loggers.get(name)
    if logger:
        return logger

    if level is None:
        level = app_config.log_level

    handler = TimedRotatingFileHandler(f'{app_config.log_path}/{name}.log', when='D', backupCount=10)
    handler.setFormatter(JSONLogFormatter(datefmt='%Y-%m-%d %H:%M:%S'))
    logger = Logger(name, level)
    logger.handlers = []
    logger.addHandler(handler)

    return logger
