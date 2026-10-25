"""Validate committed census evidence without compiling or rerunning it."""
from collections import Counter, defaultdict
import gzip
from pathlib import Path

root = Path(__file__).resolve().parent

def text(name):
    return gzip.decompress((root / (name + '.txt.gz')).read_bytes()).decode()

for size in ('80x24', '200x60'):
    events = defaultdict(Counter)
    ends = Counter()
    samples = Counter()
    mode = None
    for line in text('final-' + size).splitlines():
        w = line.split()
        if not w:
            continue
        if w[0] == 'MODE':
            mode = int(w[1])
        elif w[0] == 'B':
            events[mode][int(w[1]), int(w[2])] += 1
        elif w[0] == 'END':
            ends[mode] += 1
            assert 600 <= int(w[2]) <= 900
            assert int(w[3]) <= 5
        elif w[0] == 'S':
            samples[mode] += 1
            assert int(w[5]) <= 4
    assert ends == Counter({m: 20 for m in range(4)}), ends
    assert samples == Counter({m: 3600 for m in range(4)}), samples
    for mode, births in events.items():
        for seed in range(1, 21):
            ticks = sorted(t for s, t in births if s == seed)
            assert all(b - a >= 60 for a, b in zip(ticks, ticks[1:]))
            assert births[seed, ticks[0]] == 1
        assert all(n <= 3 and (tick >= 1800 or n == 1)
                   for (_, tick), n in births.items())
    print(size, '80 complete traversals, first bound, gap, groups and deer cap OK')
for size in ('80', '200'):
    ends = [l.split() for l in text('final-clumps-' + size).splitlines()
            if l.startswith('END ')]
    assert len(ends) == 100
    assert max(int(w[3]) for w in ends) <= 5
    print(size, '100-seed visible lurker cap OK')
for suffix in ('', '-200'):
    assert text('deer-full-before' + suffix) == text('deer-full-after' + suffix)
    print('full-health isolated deer timeline', suffix or '80', 'byte-identical')
a = [l for l in text('survival20-centred').splitlines() if 'deer=false:' in l]
b = [l for l in text('survival20-centred-no-bonus').splitlines() if 'deer=false:' in l]
assert len(a) == 20 and a == b
print('corrected no-deer final rows byte-identical with/without health bonus')
