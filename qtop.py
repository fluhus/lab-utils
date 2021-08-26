import sys
import xml.dom.minidom as xml
from collections import defaultdict
from math import log
from subprocess import PIPE, Popen
from typing import IO, List, NamedTuple, Tuple

# MEM_SIGNS = {' ': 10**6, 'M': 10**6, 'm': 10**6, 'G': 10**9, 'g': 10**9}
MEM_SIGNS = {'M': 10**6, 'm': 10**6, 'G': 10**9, 'g': 10**9}
EPS = sys.float_info.epsilon


class Job(NamedTuple):
    name: str
    owner: str
    state: str
    cpu: int
    mem: int


def aggregate_job(agg: Tuple, job: Job):
    return (agg[0] + 1, agg[1] + job.cpu, agg[2] + job.mem)


def job_stats(f: IO):
    jobs = parse_jobs(f)
    d = defaultdict(lambda: (0, 0, 0))
    for job in jobs:
        d[job.owner] = aggregate_job(d[job.owner], job)
    return d


def parse_jobs(f: IO) -> List[Job]:
    with xml.parse(f) as dom:
        dom: xml.Document
        jobs = [parse_job(e) for e in dom.getElementsByTagName('job_list')]
    jobs = [job for job in jobs if job and validate_job(job)]
    return jobs


def validate_job(job: Job) -> bool:
    if job.name == 'QRLOGIN':
        return False
    if job.state != 'r':
        return False
    if job.mem is None:
        print('Job with no memory:', job)
        return False
    if job.cpu is None:
        print('Job with no cpu:', job)
        return False
    return True


def parse_job(node: xml.Element) -> Job:
    try:
        return Job(job_name(node), job_owner(node), job_state(node), job_cpu(node),
                   job_mem(node))
    except ValueError as e:
        print('Could not parse job XML:', e)
        return None


def node_text(node: xml.Element, name: str) -> str:
    subnode = node.getElementsByTagName(name)
    if len(subnode) == 0:
        return None
    if len(subnode) > 1:
        raise ValueError(f'found {len(subnode)} nodes named "{name}",'
                         f' want 1; node:\n{node.toxml()}')
    text = subnode[0].childNodes
    assert len(text) == 1, f'found {len(text)} text nodes, want 1'
    return text[0].data


def job_state(job: xml.Element):
    return node_text(job, 'state')


def job_owner(job: xml.Element) -> str:
    return node_text(job, 'JB_owner')


def job_name(job: xml.Element) -> str:
    return node_text(job, 'JB_name')


def job_cpu(job: xml.Element) -> int:
    cpu = node_text(job, 'requested_pe')
    return int(cpu) if cpu is not None else None


def job_mem(job: xml.Element) -> int:
    raw = node_text(job, 'hard_request')
    if raw is None:
        return None
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
