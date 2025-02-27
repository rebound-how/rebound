from rich.console import Console

__all__ = ["console", "err_console"]
console = Console()
err_console = Console(stderr=True)
