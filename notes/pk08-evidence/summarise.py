"""Summarise census traces; events binned by ten seconds, deer by health."""
import sys, statistics
from collections import Counter,defaultdict
for file in sys.argv[1:]:
    first=[]; clumps=[]; counts=defaultdict(list); health=defaultdict(list); events=Counter(); groups=Counter()
    mode = 0
    wanted = int(__import__("os").environ.get("MODE", "1"))
    for line in open(file):
        w=line.split()
        if not w:continue
        if w[0]=="MODE":mode=int(w[1]);continue
        if mode != wanted:continue
        if w[0]=='END':first.append(int(w[2]));clumps.append(int(w[3]))
        if w[0]=='S':
            _,seed,tick,alive,clump,deer,hp,dead=w
            counts[int(tick)].append(int(alive)); health[int(hp)//25*25].append(int(deer))
        if w[0]=='B': groups[int(w[1]),int(w[2])]+=1
    for (seed,tick),n in groups.items():events[tick//300]+=1
    print(file)
    print('first median/range',statistics.median(first),min(first),max(first),'largest clump',max(clumps))
    for tick in (1800,3600,4320,5400):print('alive',tick,round(statistics.mean(counts[tick]),2))
    print('events per 10s', sorted(events.items()))
    print('group sizes',sorted(Counter(groups.values()).items()))
    print('deer by health [floor/25]',[(h,round(statistics.mean(v),3),len(v)) for h,v in sorted(health.items())])
