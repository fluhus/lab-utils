import re
from typing import Sequence
import numpy as np
from matplotlib import pyplot as plt
from contextlib import contextmanager

_OUTPUT_PREFIX = '/home/amitmit/Desktop/analysis/'
_IMG_SUFFIXES = ['png', 'jpg']
_IMG_RE = re.compile('|'.join('\\.' + x + '$' for x in _IMG_SUFFIXES))
_save = True


def set_save(save=True):
    global _save
    _save = save


def figure(*args, **kwargs):
    if _save:
        return plt.figure(*args, **kwargs)


def shave(file: str):
    if _save:
        if not file.startswith('/'):
            file = _OUTPUT_PREFIX + file
        plt.savefig(file)
        plt.close()
    else:
        plt.show()
    if not _IMG_RE.match(file):
        file += '.png'
    return file


def pie_params(a: Sequence):
    cmap = plt.get_cmap('Pastel1')
    return {
        'autopct': '%.0f%%',
        'colors': [cmap(i) for i in range(len(a))],
        'startangle': 90,
        'shadow': True,
        'explode': [0.03] * len(a),
        'counterclock': False,
    }


def ascii_hist(vals, h=6, w=80):
    hist, bins = np.histogram(vals, w)
    assert len(hist) == w
    ymin, ymax = min(hist), max(hist)
    ydif = ymax - ymin
    hist = [round((y - ymin) / ydif * (h - 1)) for y in hist]
    pos = {(y, i) for i, y in enumerate(hist)}
    rows = [
        ['*' if (row, col) in pos else ' ' for col in range(w)] for row in range(h)
    ]
    rows.reverse()

    x1, x2 = [f'x={x:.2g}' for x in [bins[0], bins[-1]]]
    y1, y2 = [f'y={x:.2g}' for x in [ymin, ymax]]
    x12 = '|' + x1 + (' ' * (w - len(x1) - len(x2))) + x2 + '|'

    print('-' * (w + 2))
    print('|' + y2 + (' ' * (w - len(y2))) + '|')
    [print('|' + ''.join(row) + '|') for row in rows]
    print(x12)
    print('|' + y1 + (' ' * (w - len(y1))) + '|')
    print('-' * (w + 2))
    # print('|' + ('-' * w) + '|')


@contextmanager
def ctx(f, dpi=200, sizeratio=1, **kwargs):
    """Creates a figure with dpi=200, and calls tight_layout and close at the end."""
    if 'figsize' in kwargs:
        raise KeyError('use sizeratio instead of figsize')
    if type(sizeratio) in {int, float}:
        kwargs['figsize'] = [6.4 * sizeratio, 4.8 * sizeratio]
    if type(sizeratio) in {tuple, list}:
        kwargs['figsize'] = [6.4 * sizeratio[0], 4.8 * sizeratio[1]]
    fig = figure(dpi=dpi, **kwargs)
    yield fig
    plt.tight_layout()
    print(shave(f))
