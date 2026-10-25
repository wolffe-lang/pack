"""Summarise a census run (B/D lines from the staged fixture) by spawn band
and facing: detections / births, all shadows and those born within twelve
cells (pk04's PERCEIVE + 4) of the path centre.
  python3 -I notes/pk07-evidence/summarise.py FP census.txt [census2.txt ...]
"""
import sys
from collections import defaultdict
FP = int(sys.argv[1])
BANDS = ['forest edge', 'inner verge', 'path shoulder', 'mid path']
FACES = ['down path', 'diagonal down', 'across to path', 'diagonal up', 'up path']
def band(off, half):
    if off >= half: return 0
    if off >= half - FP: return 1
    if off >= half - 3 * FP - FP // 2: return 2
    return 3
def face(fx, fy):
    if fx == 0: return 0 if fy < 0 else 4
    return 1 if fy < 0 else (2 if fy == 0 else 3)
for path in sys.argv[2:]:
    mode = None
    births = {}
    det = set()
    for line in open(path):
        w = line.split()
        if not w: continue
        if w[0] == 'MODE': mode = int(w[1]); continue
        if w[0] == 'B':
            seed, n, x, centre, half, fx, fy = map(int, w[1:8])
            births[(mode, seed, n)] = (abs(x - centre), half, fx, fy)
        elif w[0] == 'D':
            det.add((mode, int(w[1]), int(w[2])))
    print('==', path)
    for m, name in ((0, 'centre'), (1, 'far shoulder')):
        tot = defaultdict(lambda: [0, 0]); totf = defaultdict(lambda: [0, 0]); allc = [0, 0]; elig = [0, 0]
        for k, (off, half, fx, fy) in births.items():
            if k[0] != m: continue
            d = 1 if k in det else 0
            allc[0] += d; allc[1] += 1
            if off <= 12 * FP: elig[0] += d; elig[1] += 1
            b = tot[band(off, half)]; b[0] += d; b[1] += 1
            f = totf[face(fx, fy)]; f[0] += d; f[1] += 1
        pct = lambda a, b: '%d/%d %.2f%%' % (a, b, 100.0 * a / b) if b else 'n/a'
        print('  %-13s all %s   within 12 cells of centre %s' % (name, pct(*allc), pct(*elig)))
        for i, bn in enumerate(BANDS): print('    band %-14s %s' % (bn, pct(*tot[i])))
        for i, fn in enumerate(FACES): print('    face %-14s %s' % (fn, pct(*totf[i])))
