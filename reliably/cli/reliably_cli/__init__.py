import sys

__all__ = ["is_executable"]


def is_executable() -> bool:
    return getattr(sys, "oxidized", False)
