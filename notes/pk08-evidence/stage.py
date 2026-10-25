"""Stage the real simulation with birth traces, never alter gameplay.
Census: centre trot, seeds 1..20, 4320 ticks (180 seconds at 24 Hz is
incorrect: the engine is 30 Hz, so 180 seconds is 5400 ticks).
"""
import argparse, subprocess
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--revision'); p.add_argument('--seeds',type=int,default=20); p.add_argument('--mode',type=int); p.add_argument('--deer-only',action='store_true'); p.add_argument('--no-bonus',action='store_true'); p.add_argument('--no-clump',action='store_true'); p.add_argument('--size',default='80x24'); p.add_argument('--out',type=Path,required=True); p.add_argument('--survival',action='store_true'); a=p.parse_args()
root=Path(__file__).resolve().parents[2]; out=a.out.resolve(); out.mkdir(parents=True,exist_ok=True)
def source(name):
    if a.revision:
        r=subprocess.run(['git','-C',str(root),'show',a.revision+':'+name],capture_output=True,text=True)
        if r.returncode==0:return r.stdout
    return (root/name).read_text()
s=source('src/sim/sim.lu')
s=s.replace('        s.spawned += 1','        print("B {s.seed} {s.tick} {s.spawned}")\n        s.spawned += 1',1)
if a.survival:
    s=s.replace('pub struct Sim {', 'pub struct Sim {\n    probe_deer_enabled: bool,')
    s=s.replace('    Sim {\n', '    Sim {\n        probe_deer_enabled: true,',1)
    # Both old and current spawning functions get the same fixture-only guard.
    s=s.replace('fn spawn_deer(mut s: Sim) {', 'fn spawn_deer(mut s: Sim) {\n    if !s.probe_deer_enabled { return }')
if a.no_clump:
    s=s.replace('prospective_clump(s, born) > CLUMP_MAX', 'false')
    s=s.replace('prospective_clump(s, born) <= CLUMP_MAX', 'true')
if a.deer_only:
    s=s.replace('    spawn_shadows(mut s)', '    // No shadows in the full-health timeline isolation.')
    s=s.replace('    s.deer_spawned += 1', '    print("D {s.seed} {s.tick} {s.deer_spawned}")\n    s.deer_spawned += 1',1)
if a.no_bonus:
    s=s.replace('base + base * deer_bonus(s.health) / 100', 'base')
    s=s.replace('if health < HEALTH_MAX / 2 then DEER_HURT_MAX else DEER_MAX', 'DEER_MAX')
for mod in ('sim' ,'trail','world','input'):
    (out/mod).mkdir(exist_ok=True)
    (out/mod/(mod+'.lu')).write_text(s if mod=='sim' else source('src/'+mod+'/'+mod+'.lu'))
w,h=map(int,a.size.split('x'))
main=(Path(__file__).parent/'survival.lu.in').read_text() if a.survival else (Path(__file__).parent/'census.lu.in').read_text()
main=main.replace('sim.new(seed, 80, 24)',f'sim.new(seed, {w}, {h})').replace('trail.path(seed, 80,',f'trail.path(seed, {w},')
main=main.replace('seed <= 20', f'seed <= {a.seeds}')
if a.survival:
    main=main.replace('    var i = 0', '    s.probe_deer_enabled = with_deer\n    var i = 0',1)
    main=main.replace('let seeds = [11, 7, 3, 5, 16]', 'let seeds = ['+', '.join(map(str,range(1,a.seeds+1)))+']')
if a.mode is not None: main=main.replace('var mode = 0',f'var mode = {a.mode}').replace('mode < 4', f'mode < {a.mode+1}')
(out/'main.lu').write_text(main)
print('staged',out)
