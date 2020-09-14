import re
from collections import defaultdict
from subprocess import Popen, PIPE


def chain(*iters):
    return (item for it in iters for item in it)


cmd = Popen(['top', '-b', '-n', '1'], text=True, stdout=PIPE)
output = list(cmd.stdout)
splitter = re.compile('\\S+')
header = splitter.findall(output[6])
data = [splitter.findall(line) for line in output[7:]]

iusr = header.index('USER')
icpu = header.index('%CPU')
imem = header.index('%MEM')

dcpu = defaultdict(float)
dmem = defaultdict(float)

for d in data:
    dcpu[d[iusr]] += float(d[icpu])
    dmem[d[iusr]] += float(d[imem])

total_header = ('User', 'CPU', 'Memory')
total = [(usr, dcpu[usr], dmem[usr]) for usr in dcpu.keys()]
total = sorted(total, key=lambda x: x[1], reverse=True)

header_fmt = [('{:10}'.format(x) for x in total_header)]
total_fmt = (('{:10}'.format(line[0]), '{:10.1f}'.format(line[1]),
              '{:10.1f}'.format(line[2])) for line in total[:5])
print('--- BY CPU ---')
for line in chain(header_fmt, total_fmt):
    print(' '.join(line))

total = sorted(total, key=lambda x: x[2], reverse=True)

header_fmt = [('{:10}'.format(x) for x in total_header)]
total_fmt = (('{:10}'.format(line[0]), '{:10.1f}'.format(line[1]),
              '{:10.1f}'.format(line[2])) for line in total[:5])
print('\n--- BY MEMORY ---')
for line in chain(header_fmt, total_fmt):
    print(' '.join(line))
