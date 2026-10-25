"""Stage pack's eight-sector leap census, against current or baseline sim.

Build main.lu using the pinned wolf and std behind the host memory gate.
Only the staged copy disables ambient spawns and health recovery so that
one fixture-active alpha and one target remain the entire experiment.
"""
import argparse
from pathlib import Path
import subprocess

p = argparse.ArgumentParser()
p.add_argument('--revision')
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
out = a.out.resolve()
for name in ('sim', 'world', 'trail', 'input'):
    path = 'src/' + name + '/' + name + '.lu'
    text = (subprocess.check_output(['git', '-C', str(root), 'show', a.revision + ':' + path], text=True)
            if a.revision and name == 'sim' else (root / path).read_text())
    if name == 'sim':
        for anchor in ('fn spawn_shadows(mut s: Sim) {', 'fn spawn_deer(mut s: Sim) {', 'fn health_step(mut s: Sim) {'):
            assert text.count(anchor) == 1
            text = text.replace(anchor, anchor + '\n    return\n')
    (out / name).mkdir(parents=True, exist_ok=True)
    (out / path.removeprefix('src/')).write_text(text)
(out / 'main.lu').write_text((Path(__file__).parent / 'census.lu.in').read_text())
print('staged', a.revision or 'current', 'at', out)
