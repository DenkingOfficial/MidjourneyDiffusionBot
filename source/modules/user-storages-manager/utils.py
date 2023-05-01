from typing import Any


def crfname(*args: Any):
    return ".".join(map(str, args))
