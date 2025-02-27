import json
import logging
from datetime import datetime

from opentelemetry.instrumentation.logging.constants import (
    DEFAULT_LOGGING_FORMAT,
)

from reliably_app.config import Settings
from reliably_app.log import (
    DEFAULT_RICH_FMT,
    _generate_logger_config,
    _get_log_level,
    console
)


def test_parse_all_log_levels():
    _get_log_level("INFO") == logging.INFO
    _get_log_level("DEBUG") == logging.DEBUG
    _get_log_level("WARNING") == logging.WARNING
    _get_log_level("ERROR") == logging.ERROR


def test_must_be_a_valid_log_level():
    _get_log_level("BOOM") == logging.NOTSET


def test_configure_logging_with_plain_formatter(settings: Settings):
    settings.ACCESS_LOG_STDOUT = True
    settings.LOG_LEVEL = "INFO"
    settings.ACCESS_LOG_STDOUT = True
    settings.APPLICATION_LOG_STDOUT = True

    c = _generate_logger_config(settings)

    settings.APPLICATION_LOG_STDOUT = False

    assert c["disable_existing_loggers"] is False

    fmt = c["formatters"]["plain"]
    assert fmt["format"] == DEFAULT_RICH_FMT

    assert c["handlers"]["app-stdout"] == {
        "level": logging.INFO,
        "class": "rich.logging.RichHandler",
        "formatter": "plain",
        "rich_tracebacks": True,
        "show_path": False,
        "console": console
    }

    lgs = c["loggers"]
    assert lgs["reliably_app"] == {"handlers": ["app-stdout"], "level": logging.DEBUG, "propagate": False}

    assert lgs["uvicorn.access"] == {
        "handlers": ["access-stdout"],
        "propagate": False,
        "level": logging.INFO,
    }


def test_configure_logging_with_otel_enabled(settings: Settings):
    settings.OTEL_ENABLED = True
    settings.LOG_LEVEL = "INFO"
    settings.ACCESS_LOG_STDOUT = False
    settings.APPLICATION_LOG_STDOUT = False
    settings.APPLICATION_LOG_FILE = "whataver.log"
    settings.APPLICATION_LOG_FILE_LEVEL = "INFO"

    c = _generate_logger_config(settings)

    assert c["disable_existing_loggers"] is False

    fmt = c["formatters"]["plain_file"]
    assert fmt["format"] == DEFAULT_LOGGING_FORMAT

    assert c["handlers"]["app-file"]["level"] == logging.INFO
    assert c["handlers"]["app-file"]["class"] == "logging.handlers.TimedRotatingFileHandler"  # noqa
    assert c["handlers"]["app-file"]["formatter"] == "plain_file"
    assert c["handlers"]["app-file"]["filename"] == "whataver.log"
    assert c["handlers"]["app-file"]["when"] == "W0"
    assert c["handlers"]["app-file"]["backupCount"] == 4

    lgs = c["loggers"]
    assert lgs["reliably_app"] == {"handlers": ["app-file"], "level": logging.DEBUG, "propagate": False}
