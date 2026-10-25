"""Re-record a death-card replay fixture through a pty, the way pk04's were
made in a terminal: run the game on an 80x24 pty, (title: press a key),
press the debug health key ten times, wait for a shadow's fatal bite (the
death card prints `score`), save the replay with `s`, leave with `q`.
  python3 -I notes/pk07-evidence/record.py --bin target/release/pack --out FILE [--title]
Prints the recorded file's header. Nothing here traps or signals."""
import argparse, fcntl, os, pty, select, struct, sys, termios, time
ap = argparse.ArgumentParser()
ap.add_argument('--bin', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--seed', default='16')
ap.add_argument('--title', action='store_true', help='start from the title card (a key runs it)')
ap.add_argument('--timeout', type=float, default=90.0)
a = ap.parse_args()
argv = [a.bin, '--debug', '--seed', a.seed, '--tier', 'rich', '--record', a.out]
if not a.title:
    argv.append('--no-title')
pid, fd = pty.fork()
if pid == 0:
    os.execve(argv[0], argv, {'TERM': 'xterm-256color', 'HOME': os.environ.get('HOME', '/'), 'PATH': os.environ.get('PATH', '')})
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack('HHHH', 24, 80, 0, 0))
buf = b''
def pump(seconds):
    global buf
    end = time.time() + seconds
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                buf += os.read(fd, 65536)
            except OSError:
                return False
    return True
pump(1.0)
if a.title:
    os.write(fd, b' ')      # any key runs
    pump(1.0)
for _ in range(10):         # the debug key: health down by ten, a `health` event in the record
    os.write(fd, b'-')
    pump(0.08)
start = time.time()
while b'score' not in buf.split(b'\x1b[2J')[-1] and time.time() - start < a.timeout:
    pump(0.5)
dead = b'score' in buf
if not dead:
    print('no death card within the timeout', file=sys.stderr)
pump(0.5)
os.write(fd, b's')          # save the replay with its score
pump(1.0)
os.write(fd, b'q')          # leave the card (to the title, when the run began there)
pump(1.0)
if os.waitpid(pid, os.WNOHANG) == (0, 0):
    try:
        os.write(fd, b'q')  # and leave the title
    except OSError:
        pass
    pump(1.0)
_, st = os.waitpid(pid, 0)
print('exit', os.WEXITSTATUS(st) if os.WIFEXITED(st) else -1, 'dead', dead, 'bytes', len(buf))
if os.path.exists(a.out):
    print(open(a.out).read())
