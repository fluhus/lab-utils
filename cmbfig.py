"""Combines images as panels of one figure."""

import argparse
import string
from typing import List

import numpy as np
from matplotlib import pyplot as plt

FIGSIZE = np.array([6.4, 4.8])

argp = argparse.ArgumentParser()
argp.add_argument('-i', type=str, nargs='+', help='Input files')
argp.add_argument('-c', type=int, default=1, help='Number of columns')
argp.add_argument('-ht', type=float, default=1, help='Image height')
argp.add_argument('-wt', type=float, default=1, help='Image width')
argp.add_argument('-rr', type=float, nargs='*', help='Height ratios')
argp.add_argument('-cc', type=float, nargs='*', help='Width ratios')
argp.add_argument('-d', type=int, default=500, help='DPI')
argp.add_argument('-o', type=str, required=True, help='Output file')

args = argp.parse_args()

files = args.i
out = args.o
height = args.ht
width = args.wt
ncols = args.c
nrows = (len(files) + ncols - 1) // ncols
r = args.rr
c = args.cc
dpi = args.d

if r is None:
    r = [1]
if len(r) == 1:
    r = r * nrows
if c is None:
    c = [1]
if len(c) == 1:
    c = c * ncols


figsize = FIGSIZE * 0.7 * [width * ncols, height * nrows]
_, axs = plt.subplots(
    len(r),
    len(c),
    height_ratios=r,
    width_ratios=c,
    dpi=dpi,
    figsize=figsize,
    squeeze=False,
)
axes: List[plt.Axes] = [ax for axx in axs for ax in axx]
del axs
[ax.axis('off') for ax in axes]
[ax.set_title(f'{i}.', loc='left') for ax, i in zip(axes, string.ascii_uppercase)]
[ax.imshow(plt.imread(f)) for ax, f in zip(axes, files)]
plt.tight_layout()
plt.savefig(out)
plt.close()
