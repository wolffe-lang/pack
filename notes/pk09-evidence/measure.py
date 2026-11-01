#!/usr/bin/env python3
"""notes/pk09-evidence/measure.py — measurement only, never a gate.

Runs one row of a `tests/pty_rows.py` (trunk's or the lane's) through the
engine's own pty runner with every write the row makes timestamped, then
reports for each session of the aim-window row:

  written   the wall-clock gaps the ROW produced: the first arrow's last
            write to Space's write, and the second arrow's last write to
            Space's write (ms, Python's monotonic clock);
  applied   the gaps the GAME applied, from its own trace: the Space tick
            less the first arrow's and the second arrow's last applied
            press (`leap_tick`, `up_at` ... `right_at`);
  late      the game's tick lateness: each trace line's `wall_us` less its
            tick's nominal time (tick x 33 333 us), the largest and the
            median over the session;
  verdict   what the game's documented rule gives on the applied ticks
            (an arrow counts when its last press is at most 15 ticks before
            Space; the Hold from the engine's model), against what the game
            reported: a disagreement there is an aim-model fault, an
            agreement with a wrong expectation is the row's.

The forced stall: `--load N` starts N busy processes for the run (each
spins until a stop file appears, so none needs a signal); run the whole
command under `taskpolicy -c background` so the game, the row and the load
share the background clamp (the Mac has no CPU affinity; see the note).

    taskpolicy -c background python3 -I notes/pk09-evidence/measure.py \
        --rows tests/pty_rows.py --bin target/release/pack --load 12 --out DIR
"""
import argparse, gzip, importlib.machinery, importlib.util, json, os, statistics, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TICK_US = 1e6 / 30
ARROWS = {b"\x1b[A": "up", b"\x1b[B": "down", b"\x1b[D": "left", b"\x1b[C": "right"}
BIT = {"up": 1, "down": 2, "left": 4, "right": 8}
AIM_WINDOW = 15


def load(path, name):
    loader = importlib.machinery.SourceFileLoader(name, path)
    mod = importlib.util.module_from_spec(importlib.util.spec_from_loader(name, loader))
    loader.exec_module(mod)
    return mod


def trace(err):
    rows = []
    for line in err.decode(errors="replace").splitlines():
        if not line.startswith("trace tick "):
            continue
        w = line.split()
        d = {}
        for i in range(1, len(w) - 1, 2):
            try:
                d[w[i]] = int(w[i + 1])
            except ValueError:
                pass
        rows.append(d)
    return rows


def hold_until(presses):
    """The engine's Hold (lair src/input/input.lu, hold_press) over a list of
    applied press ticks: the tick the hold ends."""
    last, prev, until = -1000, -1000, -1
    for t in presses:
        gap, prev_gap = t - last, last - prev
        if gap <= 5:
            rate = gap
            if prev_gap <= 5 and prev_gap > rate:
                rate = prev_gap
            until = t + rate + 1
        elif gap <= 12 + 1:
            until = t + 5 + 1
        else:
            until = t + 12
        prev, last = last, t
    return until


def analyse(s):
    rows = trace(s.err)
    writes = [(t, d) for t, d in s.writes]
    arrows = [ARROWS[d] for _, d in writes if d in ARROWS]
    order = []
    for a in arrows:
        if a not in order:
            order.append(a)
    first = order[0] if len(order) == 2 else None
    second = order[-1] if order else None
    space = [t for t, d in writes if d == b" "]
    acc = [r for r in rows if r.get("tell") == 1]
    out = {"tier": "plain" if "plain" in s.argv else "rich", "first": first, "second": second,
           "writes": len(writes), "accepted": len(acc)}
    if not space or len(acc) != 1:
        return out
    S = acc[0]
    w_space = space[0]
    if first:
        w_first_last = max(t for t, d in writes if d in ARROWS and ARROWS[d] == first and t < w_space)
        out["written_first_ms"] = round((w_space - w_first_last) * 1000, 1)
        out["applied_first"] = S["leap_tick"] - S[first + "_at"]
    if second:
        w_second_last = max(t for t, d in writes if d in ARROWS and ARROWS[d] == second and t < w_space)
        w_second_first = min(t for t, d in writes if d in ARROWS and ARROWS[d] == second)
        out["written_second_ms"] = round((w_space - w_second_last) * 1000, 1)
        out["written_chord_ms"] = round((w_space - w_second_first) * 1000, 1)
        out["applied_second"] = S["leap_tick"] - S[second + "_at"]
    late = [r["wall_us"] - r["tick"] * TICK_US for r in rows if "wall_us" in r and r["tick"] <= S["leap_tick"] + 4]
    out["late_max_ms"] = round(max(late) / 1000, 1) if late else None
    out["late_median_ms"] = round(statistics.median(late) / 1000, 1) if late else None
    # Applied press ticks per arrow, from the per-tick trace. A trace line
    # is printed after its step, so it shows the tick already advanced: a
    # press applied on step T reads `<arrow>_at T` on the line `tick T+1`.
    # A run of one key inside a step is one press (src/sim/sim.lu, step).
    presses = {a: [r["tick"] - 1 for r in rows if r.get(a + "_at") == r["tick"] - 1 and r["tick"] - 1 <= S["leap_tick"]] for a in BIT}
    tick = S["leap_tick"]
    # An arrow applied on Space's own step may come before or after Space
    # in that step; the trace cannot say which, so the session is flagged.
    out["same_step"] = [a for a in BIT if presses[a] and presses[a][-1] == tick]
    held = sum(BIT[a] for a in BIT if presses[a] and tick < hold_until(presses[a]))
    recent = [a for a in BIT if presses[a] and (tick < hold_until(presses[a]) or tick - presses[a][-1] <= AIM_WINDOW)]
    ax = (1 if "right" in recent else 0) - (1 if "left" in recent else 0)
    ay = (1 if "up" in recent else 0) - (1 if "down" in recent else 0)
    if (ax, ay) == (0, 0):
        ax, ay = 0, 1
    out.update({"space_tick": tick, "held": S.get("leap_held"), "rule_held": held,
                "aim": (S.get("aim_x"), S.get("aim_y")), "rule_aim": (ax, ay)})
    out["game_agrees_with_rule"] = out["aim"] == out["rule_aim"] and out["held"] == out["rule_held"]
    return out


def spin(stop, seconds):
    code = ("import os, time\nend = time.monotonic() + %f\nn = 0\n"
            "while time.monotonic() < end:\n    n += 1\n"
            "    if n %% 200000 == 0 and os.path.exists(%r): break\n") % (seconds, stop)
    return subprocess.Popen([sys.executable, "-I", "-c", code])


class Raw:
    """A session read back from raw.jsonl.gz (for --reanalyse)."""
    def __init__(self, d):
        self.argv = d["argv"]
        self.writes = [(t, bytes.fromhex(h)) for t, h in d["writes"]]
        self.err = d["err"].encode()


def reanalyse(d):
    with gzip.open(os.path.join(d, "raw.jsonl.gz"), "rt") as f:
        results = [analyse(Raw(json.loads(l))) for l in f]
    with open(os.path.join(d, "sessions.jsonl"), "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    return results


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--reanalyse":
        results = reanalyse(sys.argv[2])
        bad = [r for r in results if r.get("game_agrees_with_rule") is False]
        print("measure: %d sessions re-read, %d where the game contradicts its rule" % (len(results), len(bad)))
        return 0
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True, help="the pty_rows.py to load (trunk's or the lane's)")
    ap.add_argument("--row", default="aim-window")
    ap.add_argument("--bin", required=True)
    ap.add_argument("--load", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pty = load(os.path.join(ROOT, ".lair", "tools", "pty"), "lair_pty")
    rows = load(os.path.abspath(a.rows), "rows_under_test")
    sessions = []

    class TSession(pty.Session):
        def __init__(self, argv, r, c, env):
            self.writes = []
            self.argv = argv
            pty.Session.__init__(self, argv, r, c, env)
            sessions.append(self)

        def type(self, data, settle=0.08):
            self.writes.append((time.monotonic(), data))
            os.write(self.master, data)
            self.pump(settle)

    class C(pty.Ctx):
        Session = TSession

    stop = os.path.join(a.out, "stop")
    if os.path.exists(stop):
        os.unlink(stop)
    load_procs = [spin(stop, 900) for _ in range(a.load)]
    t0 = time.monotonic()
    try:
        s, problems = rows.ROWS[a.row](os.path.abspath(a.bin), C)
    finally:
        open(stop, "w").close()
        for p in load_procs:
            p.wait()
    took = time.monotonic() - t0
    with gzip.open(os.path.join(a.out, "raw.jsonl.gz"), "wt") as f:
        for x in sessions:
            f.write(json.dumps({"argv": x.argv, "writes": [(t, d.hex()) for t, d in x.writes],
                                "err": x.err.decode(errors="replace")}) + "\n")
    results = [analyse(x) for x in sessions]
    with open(os.path.join(a.out, "sessions.jsonl"), "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(a.out, "problems.txt"), "w") as f:
        f.write("\n".join(problems) + ("\n" if problems else ""))
    disagree = [r for r in results if r.get("game_agrees_with_rule") is False]
    print("measure: %s row %s, load %d, %d sessions in %.0f s, %d problems, %d where the game contradicts its rule" % (
        a.rows, a.row, a.load, len(results), took, len(problems), len(disagree)))
    lates = [r["late_max_ms"] for r in results if r.get("late_max_ms") is not None]
    if lates:
        print("measure: tick lateness max per session: median %.1f ms, max %.1f ms" % (statistics.median(lates), max(lates)))
    over = [r for r in results if r.get("written_first_ms", 0) > 500]
    print("measure: diagonal sessions with the first arrow written more than 500 ms before Space: %d" % len(over))
    for p in problems:
        print("  - " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
