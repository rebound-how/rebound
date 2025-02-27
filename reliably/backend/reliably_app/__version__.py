from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("reliably-app")
except PackageNotFoundError:
    __version__ = "unknown"
