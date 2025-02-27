import logging
import os
import signal
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

__all__ = ["pidfile", "terminate_running_server"]

logger = logging.getLogger("reliably_app")


@contextmanager
def pidfile(path: Path, pid_file: bool = True) -> Iterator[None]:
    if pid_file is False:
        yield
    else:
        if path.exists():
            old_pid = path.read_text()
            raise IOError(f"Server already running with PID {old_pid}")

        path.write_text(str(os.getpid()))
        logger.debug(f"Pid file {path}")
        yield
        path.unlink()
        logger.debug(f"Pid file {path} removed")


def terminate_running_server(path: Path) -> None:
    if not path.exists():
        return None

    try:
        pid = int(path.read_text())
        os.kill(pid, signal.SIGTERM)
    except Exception:
        return None
    finally:
        path.unlink()
        logger.debug(f"Pid file {path} removed")
