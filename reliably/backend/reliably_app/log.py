import json
import logging
import logging.config
from pathlib import Path
from typing import Any, Callable, Dict

import orjson
from opentelemetry.instrumentation.logging.constants import (
    DEFAULT_LOGGING_FORMAT,
)
from pydantic.json import pydantic_encoder
from rich.console import Console

from reliably_app.config import Settings


__all__ = ["configure_logging", "console"]
DEFAULT_FMT = "%(asctime)s %(name)s %(levelname)s %(module)s %(message)s"
DEFAULT_RICH_FMT = "%(message)s"
logger = logging.getLogger("reliably_app")
console = Console()


def configure_logging(settings: Settings) -> None:
    """
    Configure the application's logger.
    """
    cfg = _generate_logger_config(settings)
    logging.getLogger("uvicorn").handlers.clear()
    logging.config.dictConfig(cfg)


def _get_log_level(level: str) -> int:
    """
    Maps a string log level to its numeric counterpart.

    Defaults to `logging.NOTSET` otherwise.
    """
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR

    return logging.NOTSET


def _json_dumps(
    log_record: logging.LogRecord,
    default: Callable,
    cls: json.JSONEncoder,
    indent: int | None,
    ensure_ascii: bool,
) -> str:
    return orjson.dumps(log_record, default=default).decode("utf-8")


def _generate_logger_config(settings: Settings) -> Dict[str, Any]:
    return setup_logger_config(
        log_format=settings.LOG_FORMAT,
        log_level=settings.LOG_LEVEL,
        app_log_level=settings.APPLICATION_LOG_FILE_LEVEL,
        with_otel=settings.OTEL_ENABLED,
        app_log_to_stdout=settings.APPLICATION_LOG_STDOUT,
        app_log_to_file=settings.APPLICATION_LOG_FILE,
        access_log_to_stdout=settings.ACCESS_LOG_STDOUT,
        access_log_to_file=settings.ACCESS_LOG_FILE,
        access_log_format=settings.ACCESS_LOG_LOG_FORMAT,
    )


def setup_logger_config(
    log_format: str = "plain",
    log_level: str = "INFO",
    app_log_level: str = "INGO",
    with_otel: bool = False,
    app_log_to_stdout: bool = False,
    app_log_to_file: Path | None = None,
    access_log_to_stdout: bool = False,
    access_log_to_file: Path | None = None,
    access_log_format: str = "plain",
) -> Dict[str, Any]:
    level = _get_log_level(log_level)
    app_file_log_level = _get_log_level(app_log_level)

    struct_fmt = struct_file_format = DEFAULT_FMT
    if with_otel:
        struct_fmt = struct_file_format = DEFAULT_LOGGING_FORMAT

    handler_class = "rich.logging.RichHandler"
    struct_fmt = DEFAULT_RICH_FMT

    disable_loggers()

    is_debug = level == logging.DEBUG

    cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": struct_fmt,
            },
            "json": {
                "fmt": struct_fmt,
                "json_default": pydantic_encoder,
                "json_serializer": _json_dumps,
                "json_indent": 0,
                "timestamp": True,
            },
            "plain_file": {
                "format": struct_file_format,
            },
            "access_plain_file": {
                "format": "%(message)s",
            },
            "json_file": {
                "fmt": struct_file_format,
                "json_default": pydantic_encoder,
                "json_serializer": _json_dumps,
                "json_indent": 0,
                "timestamp": True,
            },
            "access_json_file": {
                "fmt": struct_file_format,
                "json_default": pydantic_encoder,
                "json_serializer": _json_dumps,
                "json_indent": 0,
                "timestamp": True,
            },
        },
        "handlers": {},
        "loggers": {
            "": {"handlers": [], "level": logging.INFO},
            "reliably_app": {
                "handlers": [],
                "level": logging.DEBUG,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": [],
                "propagate": False,
                "level": logging.INFO,
            },
            "uvicorn.error": {
                "handlers": [],
                "propagate": False,
                "level": level,
            },
            "alembic": {
                "handlers": [],
                "propagate": False,
                "level": logging.ERROR,
            },
        },
    }

    if app_log_to_stdout:
        cfg["handlers"]["app-stdout"]: Dict = {  # type: ignore
            "level": level,
            "class": handler_class,
            "formatter": log_format,
        }

        cfg["handlers"]["app-stdout"]["rich_tracebacks"] = True  # type: ignore  # noqa
        cfg["handlers"]["app-stdout"]["console"] = console  # type: ignore
        cfg["handlers"]["app-stdout"]["show_path"] = is_debug  # type: ignore
        cfg["loggers"]["reliably_app"]["handlers"].append("app-stdout")  # type: ignore  # noqa
        cfg["loggers"]["uvicorn.error"]["handlers"].append("app-stdout")  # type: ignore  # noqa
        cfg["loggers"]["alembic"]["handlers"].append("app-stdout")  # type: ignore  # noqa

    p = app_log_to_file
    if p:
        cfg["handlers"]["app-file"]: Dict = {  # type: ignore
            "level": app_file_log_level,
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": f"{log_format}_file",
            "filename": p,
            "when": "W0",
            "backupCount": 4,
        }

        cfg["loggers"][""]["handlers"].append("app-file")  # type: ignore  # noqa
        cfg["loggers"]["reliably_app"]["handlers"].append("app-file")  # type: ignore  # noqa
        cfg["loggers"]["uvicorn.error"]["handlers"].append("app-file")  # type: ignore  # noqa
        cfg["loggers"]["alembic"]["handlers"].append("app-file")  # type: ignore  # noqa

    if access_log_to_stdout:
        cfg["handlers"]["access-stdout"]: Dict = {  # type: ignore
            "level": logging.INFO,
            "class": handler_class,
            "formatter": log_format,
        }

        cfg["handlers"]["access-stdout"]["rich_tracebacks"] = True  # type: ignore  # noqa
        cfg["handlers"]["access-stdout"]["console"] = console  # type: ignore
        cfg["handlers"]["access-stdout"]["show_path"] = False  # type: ignore
        cfg["loggers"]["uvicorn.access"]["handlers"].append("access-stdout")  # type: ignore  # noqa

    p = access_log_to_file
    if p:
        cfg["handlers"]["access-file"]: Dict = {  # type: ignore
            "level": logging.INFO,
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": f"access_{access_log_format}_file",
            "filename": p,
            "when": "W0",
            "backupCount": 4,
        }

        cfg["loggers"]["uvicorn.access"]["handlers"].append("access-file")  # type: ignore  # noqa

    return cfg


def disable_loggers() -> None:
    """
    Disable a list of loggers that may leak data or are generally not
    useful.
    """
    # leaks data at DEBUG level
    # https://github.com/python-hyper/hpack/blob/master/src/hpack/hpack.py#L126
    lgr = logging.getLogger("hpack.hpack")
    lgr.setLevel(60)
    lgr.disabled = True

    lgr = logging.getLogger("hpack.table")
    lgr.setLevel(60)
    lgr.disabled = True

    lgr = logging.getLogger("tzlocal")
    lgr.setLevel(60)
    lgr.disabled = True
