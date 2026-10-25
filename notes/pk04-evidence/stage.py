"""Stage a measurement fixture; never build or run it implicitly.

  python3 -I notes/pk04-evidence/stage.py --kind census --out target/census
  python3 -I notes/pk04-evidence/stage.py --kind parry --revision 91d93ac --out target/parry-before

Build the staged main.lu with the pinned wolf, WOLF_STD set to its bundled
std, behind the host's memory gate. --revision reads this repo's own code.
The census adds an ID and trace only, retires perceived shadows in its
controller, and stops spawns at row 1800 while draining through row 1835.
It measures sensing, not combat survival or an unsteered player.
"""
import argparse
from pathlib import Path
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument('--kind', choices=('census', 'parry'), required=True)
ap.add_argument('--revision')
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
root = Path(__file__).resolve().parents[2]
out = a.out.resolve()

def source(name):
    if a.revision:
        return subprocess.check_output(['git', '-C', str(root), 'show', a.revision + ':' + name], text=True)
    return (root / name).read_text()

s = source('src/sim/sim.lu')
main = (Path(__file__).parent / (a.kind + '.lu.in')).read_text()
if a.kind == 'census':
    if 'face_y: int' not in s:
        s = s.replace('    Shadow {\n', '    Shadow {\n        face_x: 0,\n        face_y: -2,\n')
        s = s.replace('pub struct Shadow {', 'pub struct Shadow {\n    face_x: int,\n    face_y: int,')
    s = s.replace('fn spawn_shadows(mut s: Sim) {', 'fn spawn_shadows(mut s: Sim) {\n    if alpha(s).y >= 1800 * world.FP { return }')
    s = s.replace('pub struct Shadow {', 'pub struct Shadow {\n    birth: int,')
    s = s.replace('    Shadow {\n', '    Shadow {\n        birth: s.spawned,\n')
    before = '        (mut s.shadows).push(lurker(s, top + 3 * k, side))'
    assert s.count(before) == 1, 'spawn instrumentation anchor changed'
    s = s.replace(before, '''        let born = lurker(s, top + 3 * k, side)
        let (centre, half) = world.path(s.seed, s.cols, top + 3 * k)
        print("B {s.seed} {s.spawned} {born.x} {centre} {half} {born.face_x} {born.face_y}")
        (mut s.shadows).push(born)''')
    before = '                sh.state = CHASING\n            }\n        }'
    assert before in s, 'perception instrumentation anchor changed'
    s = s.replace(before, '                print("D {s.seed} {sh.birth}")\n' + before, 1)
else:
    if 'face_y: int' not in s:
        main = main.replace('                        face_x: 0, face_y: -2, attack_age: 0,\n', '')
        main = main.replace('                        attack_dx: 0, attack_dy: -768, pose_x: 0, pose_y: 0,\n', '')
for module in ('sim', 'world'):
    (out / module).mkdir(parents=True, exist_ok=True)
(out / 'sim/sim.lu').write_text(s)
(out / 'world/world.lu').write_text(source('src/world/world.lu'))
(out / 'main.lu').write_text(main)
print('staged', a.kind, a.revision or 'working tree', 'at', out)
