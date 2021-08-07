"""
Application-wide logging configuration.
"""

import logging
import logging.config
from typing import List

import structlog
import uvicorn  # type: ignore
from starlette_context import context
from structlog.types import EventDict, WrappedLogger


def add_request_id(
    _logger: WrappedLogger, _method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Custom `structlog` processor to add request ID to `event_dict` if available.
    """

    if context.exists():
        event_dict["request_id"] = context["X-Request-ID"]

    return event_dict


shared_processors: List[structlog.types.Processor] = [
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    add_request_id,
    structlog.processors.TimeStamper(fmt="iso", utc=True),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
]

logging_dict_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(sort_keys=True),
            "foreign_pre_chain": shared_processors,
        },
        "console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.dev.ConsoleRenderer(),
            "foreign_pre_chain": shared_processors,
        },
        **uvicorn.config.LOGGING_CONFIG["formatters"],
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console",
        },
        "json_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "mode": "a",
            "maxBytes": 256 * 1024,  # 256 KiB
            "backupCount": 10,
            "encoding": "UTF-8",
            "level": "DEBUG",
            "formatter": "json",
        },
        "uvicorn.access": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "access",
        },
        "uvicorn.default": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
        "sqlalchemy.engine": {
            # INFO for logging queries
            # DEBUG for logging query results in addition to queries
            "level": "WARNING",
        },
        "uvicorn.error": {
            "handlers": ["default", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default", "json_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {  # Required for Gunicorn
        "handlers": ["default", "json_file"],
        "level": "INFO",
    },
}


def setup_logging() -> None:
    """
    Setup global logging configuration.
    """

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.config.dictConfig(logging_dict_config)
