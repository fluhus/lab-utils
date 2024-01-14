"""Common utilities."""

import gzip
import inspect
import io
import json
import os
import sys
from contextlib import contextmanager
from datetime import datetime
from time import monotonic
from typing import IO, Callable, List

import numpy as np
import pandas as pd
import scipy
from scipy.stats import gaussian_kde, pearsonr, spearmanr


def printerr(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def is_interactive() -> bool:
    """Indicates whether this run is batch or interactive shell."""
    return hasattr(sys, "ps1")


def flatten(a):
    """Flattens a list or an iterable."""
    if isinstance(a, list):
        return [c for b in a for c in b]
    return (c for b in a for c in b)


def mylog(*args):
    fr = inspect.currentframe().f_back
    ln = fr.f_lineno
    fl = fr.f_code.co_filename
    print(f'{fl}:{ln}', file=sys.stderr)
    print('AMIT:', *args, file=sys.stderr)


def timers():
    c = {a * 10**b for a in range(1, 10) for b in range(10)}
    i = 0
    t = datetime.now()

    def inc():
        nonlocal c, i, t
        i += 1
        if i in c:
            d = datetime.now() - t
            print(f'\r{d} ({d/i}) {i}', end='')

    def done():
        nonlocal t, i
        d = datetime.now() - t
        if i == 0:
            print(f'\r{d}')
        else:
            print(f'\r{d} ({d/i}) {i}')

    return inc, done


@contextmanager
def timing(msg=None):
    if msg:
        print(msg)
    inc, done = timers()
    yield inc
    done()


def zopen(path: str, mode: str = 'rt') -> IO:
    """Opens a file for I/O. If path has a gz/gzip suffix, uses the gzip
    library."""
    if path.endswith('.gz') or path.endswith('.gzip'):
        if mode.startswith('w'):
            return gzip.open(path, mode, compresslevel=1)
        return gzip.open(path, mode)
    return open(path, mode)


def benchmark(f: Callable, internal_loop=False):
    """Calls f in a loop and prints timing results."""
    n = 1
    diff = 0
    while diff < 2:
        t = monotonic()
        if internal_loop:
            f(n)
        else:
            for _ in range(n):
                f()
        diff = monotonic() - t
        n = int(n * 1.5 + 0.5)
    print(f'{n} iterations {diff:.1f}s ({diff/n:.1e}s / iteration)')


def assert_type(val, typ):
    if not isinstance(val, typ):
        raise TypeError(f'received type {type(val)}, expected {typ}')


def assert_dtype(val, typ):
    if str(val.dtype) != str(typ):
        raise TypeError(f'received type {val.dtype}, expected {typ}')


def force_remove(f: str):
    try:
        os.remove(f)
    except FileNotFoundError:
        pass  # Ok


def steps13(n) -> List[int]:
    return [m * 10**e for e in range(n + 1) for m in [1, 3]]


def steps125(n) -> List[int]:
    return [m * 10**e for e in range(n + 1) for m in [1, 2, 5]]


def gaussian_thingie(vals):
    xx = np.linspace(min(vals), max(vals), 1001)
    return xx, gaussian_kde(vals)(xx)


def pearson(a, b, p=False):
    s = pearsonr(a, b)
    if p:
        return s.statistic, s.pvalue
    return s.statistic


def spearman(a, b, p=False):
    s = spearmanr(a, b)
    if p:
        return s.correlation, s.pvalue
    return s.correlation


def f1(a: set, b: set):
    prc = len(a & b) / len(a)
    rcl = len(a & b) / len(b)
    return 2 * prc * rcl / (prc + rcl)


def save_sparse_df(df: pd.DataFrame, f: IO):
    """Saves a sparse dataframe as JSON."""
    buf = io.BytesIO()
    scipy.sparse.save_npz(buf, df.sparse.to_coo())
    buf = buf.getvalue().hex()
    json.dump(
        {
            'data': buf,
            'cols': df.columns.tolist(),
            'rows': df.index.tolist(),
            'inames': list(df.index.names),
        },
        f,
    )


def load_sparse_df(f: IO) -> pd.DataFrame:
    """Loads a sparse dataframe from JSON."""
    data = json.load(f)
    df = pd.DataFrame.sparse.from_spmatrix(
        scipy.sparse.load_npz(io.BytesIO(bytes.fromhex(data['data'])))
    )
    df.columns, df.index = (data['cols'], data['rows'])
    df.index.names = data['inames']
    return df
