"""Caching functionality."""

import json
import os
from typing import Callable


def cached(f: str):
    def bla(fn: Callable):
        def wrapper(*args, cache_force=False, **kwargs):
            if not cache_force and os.path.exists(f):
                return json.load(open(f))
            print('Creating cache for:', fn.__name__)
            x = fn(*args, **kwargs)
            json.dump(x, open(f, 'w'))
            return x

        return wrapper

    return bla
