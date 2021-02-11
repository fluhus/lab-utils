import re
import sys
from collections import defaultdict
from math import log
from subprocess import PIPE, Popen
from typing import IO, List

ITEM_RE = re.compile('^\\s*\\d')
NAME_RE = re.compile('^\\s*\\S+\\s+\\S+\\s+\\S+\\s+(\\S+)')
MEM_RE = re.compile('mem_free=(\\d+)(.)')
CPU_RE = re.compile('\\sthreads (\\d+)\\s')

MEM_SIGNS = {'M': 10**6, 'm': 10**6, 'G': 10**9, 'g': 10**9}
EPS = sys.float_info.epsilon


def parse_item(lines: List):
    cat = ' '.join(lines)
    return extract_user(cat), 1, extract_cpu(cat), extract_mem(cat)


def extract_user(s: str) -> str:
    m = NAME_RE.match(s)
    if not m:
        raise ValueError('Could not find username: ' + s)
    return m.group(1)


def extract_mem(s: str) -> int:
    m = MEM_RE.findall(s)
    if not m:
        return 0
    return int(m[0][0]) * MEM_SIGNS[m[0][1]]


def extract_cpu(s: str) -> int:
    m = CPU_RE.findall(s)
    if not m:
        return 0
    return int(m[0][0])


def parse_items(f: IO):
    # Skip header.
    next(f)
    next(f)

    current = []
    for line in f:
        if not ITEM_RE.match(line):
            assert current, f'Bad line (expected item header): {line}'
            current.append(line.strip())
            continue
        if current:
            yield parse_item(current)
        current = [line.strip()]
    if current:
        yield parse_item(current)


def tupsum(t1, t2):
    return tuple(t1[i] + t2[i] for i in range(len(t1)))


def collect_items(f: IO):
    d = defaultdict(lambda: (0, 0, 0))
    for item in parse_items(f):
        d[item[0]] = tupsum(d[item[0]], item[1:])
    return d


def main():
    cmd = Popen(['qstat', '-r', '-u', '*'], text=True, stdout=PIPE)
    col = collect_items(cmd.stdout)
    names = sorted(col.keys(),
                   key=lambda k: -sum(log(x + EPS) for x in col[k]))

    print('User\tJobs\tCPU\tMem')
    for name in names[:5]:
        x = col[name]
        print(f'{name}\t{x[0]}\t{x[1]}\t{int(x[2] / 10 ** 9)}G')


if __name__ == '__main__':
    main()
