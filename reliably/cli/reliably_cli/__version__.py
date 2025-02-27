from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("reliably-cli")
except PackageNotFoundError:
    __version__ = "unknown"
