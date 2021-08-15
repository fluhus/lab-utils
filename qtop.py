import sys
import xml.dom.minidom as xml
from collections import defaultdict
from math import log
from subprocess import PIPE, Popen
from typing import IO, List, Tuple

MEM_SIGNS = {' ': 10**6, 'M': 10**6, 'm': 10**6, 'G': 10**9, 'g': 10**9}
EPS = sys.float_info.epsilon


def tupsum(t1, t2):
    return tuple(t1[i] + t2[i] for i in range(len(t1)))


def job_stats(f: IO):
    jobs = parse_jobs(f)
    d = defaultdict(lambda: (0, 0, 0))
    for job in jobs:
        d[job[0]] = tupsum(d[job[0]], job[1:])
    return d


def parse_jobs(f: IO) -> List[Tuple]:
    with xml.parse(f) as dom:
        dom: xml.Document
        jobs = dom.getElementsByTagName('job_list')
        jobs = [
            job for job in jobs if job_name(job) != 'QRLOGIN' and job_is_running(job)
        ]
        return [(job_owner(j), 1, job_cpu(j), job_mem(j)) for j in jobs]


def node_text(node: xml.Element, name: str) -> str:
    subnode = node.getElementsByTagName(name)
    assert len(subnode) == 1, f'found {len(subnode)} nodes named "{name}", want 1'
    text = subnode[0].childNodes
    assert len(text) == 1, f'found {len(text)} text nodes, want 1'
    return text[0].data


def job_is_running(job: xml.Element):
    return node_text(job, 'state') == 'r'


def job_owner(job: xml.Element) -> str:
    return node_text(job, 'JB_owner')


def job_name(job: xml.Element) -> str:
    return node_text(job, 'JB_name')


def job_cpu(job: xml.Element) -> str:
    return int(node_text(job, 'requested_pe'))


def job_mem(job: xml.Element) -> str:
    raw = node_text(job, 'hard_request')
    if '0' <= raw[-1] <= '9':  # Default is megabytes.
        raw += 'M'
    return int(raw[:-1]) * MEM_SIGNS[raw[-1]]


def main():
    cmd = Popen(['qstat', '-xml', '-r', '-u', '*'], text=True, stdout=PIPE)
    col = job_stats(cmd.stdout)
    names = sorted(col.keys(), key=lambda k: -sum(log(x + EPS) for x in col[k]))

    print('User\tJobs\tCPU\tMem')
    for name in names[:5]:
        x = col[name]
        print(f'{name}\t{x[0]}\t{x[1]}\t{int(x[2] / 10 ** 9)}G')


if __name__ == '__main__':
    main()
