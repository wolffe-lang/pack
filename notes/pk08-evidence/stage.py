"""Stage the real simulation with birth traces, never alter gameplay.
Census: centre trot, seeds 1..20, 4320 ticks (180 seconds at 24 Hz is
incorrect: the engine is 30 Hz, so 180 seconds is 5400 ticks).
"""
import argparse, subprocess
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--revision'); p.add_argument('--size',default='80x24'); p.add_argument('--out',type=Path,required=True); p.add_argument('--survival',action='store_true'); a=p.parse_args()
root=Path(__file__).resolve().parents[2]; out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
def source(name):
    if a.revision:
        r=subprocess.run(['git','-C',str(root),'show',a.revision+':'+name],capture_output=True,text=True)
        if r.returncode==0:return r.stdout
    return (root/name).read_text()
s=source('src/sim/sim.lu')
s=s.replace('        s.spawned += 1','        print("B {s.seed} {s.tick} {s.spawned}")\n        s.spawned += 1',1)
for mod in ('sim','trail','world','input'):
    (out/mod).mkdir(exist_ok=True)
    (out/mod/(mod+'.lu')).write_text(s if mod=='sim' else source('src/'+mod+'/'+mod+'.lu'))
w,h=map(int,a.size.split('x'))
main=(Path(__file__).parent/'survival.lu.in').read_text() if a.survival else (Path(__file__).parent/'census.lu.in').read_text()
main=main.replace('sim.new(seed, 80, 24)',f'sim.new(seed, {w}, {h})').replace('trail.path(seed, 80,',f'trail.path(seed, {w},')
(out/'main.lu').write_text(main)
print('staged',out)
