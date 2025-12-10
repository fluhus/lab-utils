"""Compares two abundance files."""

import argparse
import csv
import json
import math
from typing import Dict

import commute
import myplot
from matplotlib import pyplot as plt


def load_abundance(f: str):
    if f.endswith('.json'):
        return json.load(open(f))
    lines = csv.reader(open(f), delimiter='\t')
    return {a: float(b) for a, b, *_ in lines}


def harmean(a):
    a = [1 / x for x in a]
    m = sum(a) / len(a)
    return 1 / m


def compare(
    real: Dict[str, float],
    est: Dict[str, float],
    out: str,
    print_fp=False,
    print_fn=False,
    for_thesis=False,
    title=None,
):
    union = list(set(real) | set(est))
    intr = list(set(real) & set(est))
    aa = [real.get(x, 0) for x in union]
    bb = [est.get(x, 0) for x in union]
    prs, spr = commute.pearson(aa, bb), commute.spearman(aa, bb)
    print(f'Lin: {prs:.2f} {spr:.2f}')
    aal = [math.log10(real[x]) for x in intr]
    bbl = [math.log10(est[x]) for x in intr]
    prs, spr = commute.pearson(aal, bbl), commute.spearman(aal, bbl)
    print(f'Log: {prs:.2f} {spr:.2f}')
    fp = len(set(est) - set(real)) / len(est)
    fn = len(set(real) - set(est)) / len(real)
    ntp = len(set(real) & set(est))
    rcl = ntp / len(real)
    prc = ntp / len(est)
    f1 = harmean([rcl, prc])
    print(f'FP={fp:.2f} FN={fn:.2f} F1={f1:.2f}')

    if for_thesis:
        plt.style.use('bmh')
        with myplot.ctx(out):
            plt.scatter(aal, bbl)
            plt.xlabel('Log10 real abundance')
            plt.ylabel('Log10 estimated abundance')

            for k in set(est) - set(real):
                if est[k] == 0:
                    continue
                plt.axhline(math.log10(est[k]), alpha=0.3, ls=':', color='red')
            for k in set(real) - set(est):
                if real[k] == 0:
                    continue
                plt.axvline(math.log10(real[k]), alpha=0.3, ls=':', color='red')

            if title:
                plt.title(
                    title.format(
                        prs=prs, spr=spr, fp=fp, fn=fn, prc=prc, rcl=rcl, f1=f1
                    )
                )
    else:
        with myplot.ctx(out, sizeratio=(2, 1)):
            plt.subplot(1, 2, 1)
            plt.scatter(aa, bb)
            plt.xlabel('Real')
            plt.ylabel('Estimated')
            plt.title('Linear')

            plt.subplot(1, 2, 2)
            plt.scatter(aal, bbl)
            plt.xlabel('Real')
            plt.ylabel('Estimated')
            plt.title(f'Log10, FP={fp*100:.0f}%, FN={fn*100:.0f}%')

            for k in set(est) - set(real):
                plt.axhline(math.log10(est[k]), alpha=0.3, ls=':', color='red')
            for k in set(real) - set(est):
                plt.axvline(math.log10(real[k]), alpha=0.3, ls=':', color='red')

    if print_fn:
        print('False-negatives:', ','.join(sorted(set(real) - set(est))))

    if print_fp:
        print('False-positives:', ','.join(sorted(set(est) - set(real))))


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('-r', type=str, required=True, help='Real abundance')
    argp.add_argument('-e', type=str, required=True, help='Estimated abundance')
    argp.add_argument('-fn', action='store_true', help='Print false-negatives')
    argp.add_argument('-fp', action='store_true', help='Print false-positives')
    argp.add_argument('-th', action='store_true', help='Figure for thesis')
    argp.add_argument('-o', type=str, default='cmpabnd', help='Output file')
    argp.add_argument('-t', type=str, help='Plot title')
    args = argp.parse_args()
    r = load_abundance(args.r)
    e = load_abundance(args.e)
    compare(r, e, args.o, args.fp, args.fn, for_thesis=args.th, title=args.t)


if __name__ == '__main__':
    main()
