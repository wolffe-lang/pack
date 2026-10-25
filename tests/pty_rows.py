"""tests/pty_rows.py — pack's own pty rows, loaded by the engine's runner
(`.lair/tools/pty`) by path. Each row takes the binary and the runner's
context (its Session, env_for, common_checks, screen_text and ROOT) and
returns (session, problems), as the engine's rows do.

  held-run    the input drift the maintainer felt (pk01): Left typed as a
              held key, one `ESC [ D` every 33 ms for a second (a terminal's
              autorepeat; there is no key-up), then nothing. Under `--trace`
              the game prints one line a tick; the row reads the tick of the
              last byte and asserts that the heading stops turning further
              within HELD_STOP_TICKS of it and is straight again, the wolf's
              column at rest, within HELD_STRAIGHT_TICKS: the hold ends when
              the repeats end, and the heading returns at the turn rate, not
              by a slow relaxation.
  card        the complete loop (pk02): `--seed 16 --debug --trace --record
              target/pty/card.pk --no-title`, the debug key `-` typed ten
              times (health to zero: the alpha alone), the shadows' first
              landed attack ends the run (the trace's `dead 1`), then `s`
              saves the replay and `q` leaves: exit 0 and the restore
              assertions; the closing line names the death and the saved
              file; the saved `.pk` parses, ends with the quit, and re-run
              headless twice gives byte-identical frames; the screen captured
              before `s` (the card) equals the headless final frame of the
              saved replay, cell for cell: a replay reproduces the run
              through its death.
  title       the title card (pk03), under a HOME of its own (target/pty/home,
              so the maintainer's ~/.pack/best is never touched): the game
              starts on the title (`any key to run` captured), `r` runs seed
              16 under --debug --trace --record, `-` ten times, the death, `s`
              saves the replay (with its score comment), `q` returns to the
              title (the last score and the saved name shown, the best file
              written with them), `r` runs the SAME seed again (the trace's
              tick count restarts; the closing lines name seed 16 twice),
              `q` back to the title, `p` plays the saved replay (its card
              says `verified`), `q` to the title, `q` leaves: exit 0 and the
              restore assertions.
"""
import os, subprocess, time


# The held-run row's bars, in ticks after the last byte's tick: the heading
# stops turning further (the hold ended: one repeat interval plus the margin)
# and the heading is straight with the column at rest (the turn rate's
# return, no slow relaxation). The old model relaxed one unit a tick and
# left the heading off-axis for two seconds after the last byte.
HELD_STOP_TICKS = 2
HELD_STRAIGHT_TICKS = 10


def trace_ticks(err):
    """The per-tick trace lines as dicts (tick, in, keys, steer, heading, x, y)."""
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


def row_held_run(bin, ctx):
    Session, env_for, common_checks, screen_text, ROOT = ctx.Session, ctx.env_for, ctx.common_checks, ctx.screen_text, ctx.ROOT
    s = Session([bin, "--seed", "7", "--trace", "--no-title"], 24, 80, env_for())
    s.pump(0.5)
    # A held Left: the autorepeat stream a terminal sends, one sequence a
    # tick for a second (30 bytes groups), then release.
    t_end = time.monotonic() + 1.0
    n = 0
    while time.monotonic() < t_end:
        os.write(s.master, b"\x1b[D")
        n += 1
        s.pump(0.033)
    s.pump(3.0)
    s.type(b"q")
    s.finish()
    problems = []
    common_checks(s, 0, problems)
    rows = trace_ticks(s.err)
    if len(rows) < 60:
        problems.append("only %d trace lines; is --trace printing?" % len(rows))
        return s, problems
    fed = [r for r in rows if r.get("keys", 0) > 0]
    if not fed:
        problems.append("no tick applied a key: %r" % s.err[-300:])
        return s, problems
    last = fed[-1]["tick"]
    after = [r for r in rows if r["tick"] > last]
    # 1. The heading stops turning further within HELD_STOP_TICKS.
    peak = max(abs(r["heading"]) for r in rows if r["tick"] <= last + HELD_STOP_TICKS)
    turned_more = [r["tick"] for r in after if r["tick"] > last + HELD_STOP_TICKS and abs(r["heading"]) > peak]
    if turned_more:
        problems.append("the heading kept turning after tick %d + %d (first at %d, |heading| %d over %d)" % (
            last, HELD_STOP_TICKS, turned_more[0], max(abs(r["heading"]) for r in after), peak))
    # 2. Straight, and the column at rest, within HELD_STRAIGHT_TICKS.
    straight_at = next((r["tick"] for r in after if r["heading"] == 0), None)
    if straight_at is None or straight_at > last + HELD_STRAIGHT_TICKS:
        problems.append("the heading was not straight within %d ticks of the last byte (tick %d): straight at %s; headings %s" % (
            HELD_STRAIGHT_TICKS, last, straight_at, [r["heading"] for r in after[:40]]))
    xs = [r["x"] for r in after if r["tick"] >= last + HELD_STRAIGHT_TICKS]
    rest_at = None
    for i in range(1, len(after)):
        if all(r["x"] == after[i]["x"] for r in after[i:]):
            rest_at = after[i]["tick"]
            break
    if xs and len(set(xs)) != 1:
        problems.append("the column still moved after tick %d + %d: x %s" % (last, HELD_STRAIGHT_TICKS, sorted(set(xs))[:6]))
    s.evidence = "%d sequences typed, last key at tick %d, peak |heading| %d, straight at %s, column at rest at %s" % (
        n, last, peak, straight_at, rest_at)
    return s, problems


def row_card(bin, ctx):
    Session, env_for, common_checks, screen_text, ROOT = ctx.Session, ctx.env_for, ctx.common_checks, ctx.screen_text, ctx.ROOT
    d = os.path.join(ROOT, "target", "pty")
    os.makedirs(d, exist_ok=True)
    rec = os.path.join(d, "card.pk")
    if os.path.exists(rec):
        os.unlink(rec)
    s = Session([bin, "--seed", "16", "--debug", "--trace", "--record", rec, "--no-title"], 24, 80, env_for())
    s.pump(0.4)
    for _ in range(10):
        s.type(b"-", settle=0.04)
    # Wait for the death: the trace line says `dead 1` once the first landed
    # attack ends the run (seed 16: within about ten seconds).
    end = time.monotonic() + 40.0
    while time.monotonic() < end and b" dead 1 " not in s.err:
        s.pump(0.2)
    problems = []
    if b" dead 1 " not in s.err:
        s.type(b"q")
        s.finish()
        problems.append("the run did not end within 40 s: %r" % s.err[-300:])
        return s, problems
    s.pump(0.3)
    before_save = len(s.out)
    s.type(b"s", settle=0.3)
    s.type(b"q")
    s.finish()
    common_checks(s, 0, problems)
    closing = [l for l in s.err.decode(errors="replace").splitlines() if l.startswith("pack: ended")]
    line = closing[-1] if closing else ""
    if "dead at tick" not in line:
        problems.append("the closing line does not name the death: %r" % line[-300:])
    if ("saved %s" % rec) not in line:
        problems.append("the closing line does not name the saved file: %r" % line[-300:])
    if not os.path.exists(rec):
        problems.append("no replay at %s" % rec)
        return s, problems
    text = open(rec, encoding="utf-8").read()
    events = [l for l in text.splitlines() if l.startswith("t ")]
    if not events or events[-1].split()[2] != "quit":
        problems.append("the saved replay does not end with the quit: %r" % events[-3:])
        return s, problems
    if not any(l.split()[2] == "health" for l in events):
        problems.append("the saved replay carries no health event: %r" % events[:3])
    last_tick = int(events[-1].split()[1])
    frames = str(last_tick + 1)
    # The saved replay, re-run twice: byte-identical frames (the complete
    # loop reproduces).
    outs = []
    for n in (1, 2):
        hd = os.path.join(d, "card-rerun-%d" % n)
        run = subprocess.run([bin, "--headless", "--script", rec, "--frames", frames, "--every", "25",
                              "--tier", "rich", "--dump", hd], capture_output=True)
        if run.returncode != 0:
            problems.append("the headless re-run %d failed: %r" % (n, run.stderr[-200:]))
            return s, problems
        outs.append(hd)
    cmp = subprocess.run(["diff", "-r", outs[0], outs[1]], capture_output=True)
    if cmp.returncode != 0:
        problems.append("the two re-runs differ: %r" % cmp.stdout[:300])
    # The card the player saw (the capture up to the save) equals the
    # headless final frame of the saved replay.
    cap = os.path.join(d, "card.bin")
    with open(cap, "wb") as f:
        f.write(s.out[:before_save])
    applied = subprocess.run([bin, "--apply", cap, "--size", "80x24"], capture_output=True)
    if applied.returncode != 0:
        problems.append("--apply failed: %r" % applied.stderr[-200:])
        return s, problems
    text_pty, sty_pty, _ = applied.stdout.decode("utf-8").split("--\n")
    want_text = open(os.path.join(outs[0], "final.txt"), encoding="utf-8").read()
    want_sty = open(os.path.join(outs[0], "final.sty"), encoding="utf-8").read()
    if "the pack is gone" not in text_pty:
        problems.append("the captured screen shows no card")
    if text_pty != want_text:
        for i, (a, b) in enumerate(zip(text_pty.splitlines(), want_text.splitlines())):
            if a != b:
                problems.append("the card differs from the replay's at row %d:\n  pty    %r\n  replay %r" % (i, a, b))
                break
        else:
            problems.append("glyphs differ in length")
    if sty_pty != want_sty:
        problems.append("the card's styles differ from the replay's")
    s.evidence = "death in the trace, %d events saved, last tick %d, re-run twice identical" % (len(events), last_tick)
    return s, problems



def row_title(bin, ctx):
    Session, env_for, common_checks, screen_text, ROOT = ctx.Session, ctx.env_for, ctx.common_checks, ctx.screen_text, ctx.ROOT
    d = os.path.join(ROOT, "target", "pty")
    home = os.path.join(d, "home")
    import shutil
    shutil.rmtree(home, ignore_errors=True)
    os.makedirs(home)
    rec = os.path.join(d, "title.pk")
    if os.path.exists(rec):
        os.unlink(rec)
    env = env_for()
    env["HOME"] = home
    s = Session([bin, "--seed", "16", "--debug", "--trace", "--record", rec], 24, 80, env)
    s.pump(0.6)
    problems = []
    first = screen_text(bin, s.out)
    if "any key to run" not in first or "p a c k" not in first:
        problems.append("the title card is not on the first screen: %r" % first[:400])
    if "best   -" not in first:
        problems.append("a fresh HOME shows no best: %r" % [l for l in first.splitlines() if "best" in l])
    # r: the same seed runs; the trace starts.
    s.type(b"r", settle=0.5)
    for _ in range(10):
        s.type(b"-", settle=0.04)
    end = time.monotonic() + 40.0
    while time.monotonic() < end and b" dead 1 " not in s.err:
        s.pump(0.2)
    if b" dead 1 " not in s.err:
        s.type(b"q"); s.type(b"q")
        s.finish()
        problems.append("the first run did not end within 40 s: %r" % s.err[-300:])
        return s, problems
    s.pump(0.3)
    s.type(b"s", settle=0.3)
    before_q = len(s.out)
    s.type(b"q", settle=0.6)
    title2 = screen_text(bin, s.out)
    if "any key to run" not in title2:
        problems.append("q on the card did not return to the title: %r" % title2[:400])
    if "saved  title.pk" not in title2:
        problems.append("the title does not name the saved replay: %r" % [l for l in title2.splitlines() if "saved" in l or "last" in l])
    closing1 = [l for l in s.err.decode(errors="replace").splitlines() if l.startswith("pack: ended")]
    if len(closing1) != 1 or "dead at tick" not in closing1[0] or "seed 16" not in closing1[0]:
        problems.append("one closing line for the first run, dead, seed 16: %r" % closing1)
    score = None
    for w in closing1[0].split(";") if closing1 else []:
        if "score" in w:
            try:
                score = int(w.split("score")[-1].strip().split()[0].rstrip(","))
            except ValueError:
                pass
    if score is None:
        problems.append("no score in the closing line: %r" % closing1)
    else:
        if ("last   %d" % score) not in title2:
            problems.append("the title's last score is not %d: %r" % (score, [l for l in title2.splitlines() if "last" in l]))
        if ("best   %d" % score) not in title2:
            problems.append("the title's best is not %d" % score)
    bestfile = os.path.join(home, ".pack", "best")
    if not os.path.exists(bestfile):
        problems.append("no best file at %s" % bestfile)
    else:
        text = open(bestfile, encoding="utf-8").read()
        if score is not None and ("best %d 16 " % score) not in text:
            problems.append("the best file does not record the score: %r" % text)
        if ("saved %s" % rec) not in text:
            problems.append("the best file does not name the saved replay: %r" % text)
    if not os.path.exists(rec):
        problems.append("no replay at %s" % rec)
        s.type(b"q"); s.finish()
        return s, problems
    rtext = open(rec, encoding="utf-8").read()
    if score is not None and ("# score %d" % score) not in rtext:
        problems.append("the saved replay carries no score comment: %r" % rtext[:200])
    # r again: the SAME seed, the trace restarting at tick 1.
    err_before = len(s.err)
    s.type(b"r", settle=1.0)
    s.type(b"q", settle=0.6)
    tail = s.err[err_before:].decode(errors="replace")
    if "trace tick 1 " not in tail:
        problems.append("the second run's trace does not restart at tick 1")
    closing2 = [l for l in s.err.decode(errors="replace").splitlines() if l.startswith("pack: ended")]
    if len(closing2) != 2 or "seed 16" not in closing2[1] or "ended by the quit key" not in closing2[1]:
        problems.append("the second run: seed 16 again, ended by q: %r" % closing2[-1:])
    # p: the saved replay plays to its card, verified.
    s.type(b"p", settle=0.5)
    end = time.monotonic() + 40.0
    while time.monotonic() < end and b"replay score" not in s.err and len([l for l in s.err.decode(errors="replace").splitlines() if l.startswith("pack: ended")]) < 3:
        s.pump(0.2)
    s.pump(0.3)
    # The replay ended at its recorded quit and returned to the title; the
    # title's message names the verdict. One more q leaves.
    title3 = screen_text(bin, s.out)
    if "verified" not in title3:
        problems.append("the title does not report the replay verified: %r" % [l for l in title3.splitlines() if "verif" in l or "last" in l])
    s.type(b"q")
    s.finish()
    common_checks(s, 0, problems)
    closing = [l for l in s.err.decode(errors="replace").splitlines() if l.startswith("pack: ended")]
    if len(closing) != 3 or "replay score" not in closing[2] or "verified" not in closing[2]:
        problems.append("three runs, the third a verified replay: %r" % closing[-1:])
    s.evidence = "score %s; %d closing lines; best file %s" % (score, len(closing), "written" if os.path.exists(bestfile) else "missing")
    return s, problems


def row_directional_chords(bin, ctx):
    """Real decoder -> held chord -> one-tick tell on each tier, restored."""
    problems = []
    cases = [(b"", "N"), (b"\x1b[A", "N"),
             (b"\x1b[A\x1b[C", "NE"), (b"\x1b[C", "E"),
             (b"\x1b[B\x1b[C", "SE"), (b"\x1b[B", "S"),
             (b"\x1b[B\x1b[D", "SW"), (b"\x1b[D", "W"),
             (b"\x1b[A\x1b[D", "NW")]
    count = 0
    for tier in ("rich", "plain"):
        for arrows, name in cases:
            s = ctx.Session([bin, "--seed", "7", "--tier", tier, "--no-title"],
                            24, 80, ctx.env_for())
            s.type(arrows + b" ", settle=0.4)
            # The tell is gone after one tick; its bytes remain in the capture.
            if ("Leap " + name).encode() not in s.out:
                problems.append("%s %s: no aimed tell in the live output" % (tier, name))
            s.type(b"q")
            s.finish()
            ctx.common_checks(s, 0, problems)
            count += 1
    s.evidence = "%d fresh terminal sessions: default plus eight held aims, both tiers" % count
    return s, problems


def row_aim_window(bin, ctx):
    """One key repeats at a time: first arrow, then only the second, Space."""
    arrows = {"up": b"\x1b[A", "down": b"\x1b[B", "left": b"\x1b[D", "right": b"\x1b[C"}
    cases = [("up", "right", 1, 1), ("right", "up", 1, 1),
             ("up", "left", -1, 1), ("left", "up", -1, 1),
             ("down", "right", 1, -1), ("right", "down", 1, -1),
             ("down", "left", -1, -1), ("left", "down", -1, -1)]
    cases = [(a, b, x, y, delay) for a, b, x, y in cases for delay in (0.2, 0.3, 0.4)]
    cases += [(None, name, x, y, 0.3) for name, x, y in
              [("up", 0, 1), ("down", 0, -1), ("left", -1, 0), ("right", 1, 0)]]
    cases += [(None, None, 0, 1, 0.3)]
    problems, evidence = [], []
    for tier in ("rich", "plain"):
        for first, second, x, y, delay in cases:
            s = ctx.Session([bin, "--seed", "7", "--tier", tier, "--trace", "--no-title"],
                            24, 80, ctx.env_for())
            if first:
                # Initial delay, then autorepeat. After this there are NO
                # more bytes from the first arrow (last-key-only repeat).
                s.type(arrows[first], settle=0.25)
                for _ in range(5):
                    s.type(arrows[first], settle=0.05)
            second_at = time.monotonic()
            if second:
                # Absolute deadlines avoid accumulating select's rounding
                # at each repeat into a longer-than-requested chord delay.
                for n in range(round(delay / 0.05)):
                    s.type(arrows[second], settle=0)
                    s.pump(max(0, second_at + (n + 1) * 0.05 - time.monotonic()))
            else:
                s.pump(delay)
            elapsed_ms = round((time.monotonic() - second_at) * 1000)
            s.type(b" ", settle=0.12)
            accepted = [r for r in trace_ticks(s.err) if r.get("tell") == 1]
            tag = "%s %s>%s delay=%dms actual=%dms" % (tier, first, second, round(delay * 1000), elapsed_ms)
            if len(accepted) != 1:
                problems.append("%s: accepted Space rows %r" % (tag, accepted))
            else:
                r = accepted[0]
                raw = r.get("leap_held")
                actual = (r.get("aim_x"), r.get("aim_y"))
                row = "%s Space=%s held=%s aim=%s,%s up_at=%s down_at=%s left_at=%s right_at=%s" % (
                    tag, r.get("leap_tick"), raw, *actual, r.get("up_at"), r.get("down_at"),
                    r.get("left_at"), r.get("right_at"))
                evidence.append(row)
                expected_held = {"up": 1, "down": 2, "left": 4, "right": 8, None: 0}[second]
                if raw != expected_held:
                    problems.append("%s: fixture Hold set is not the last key alone" % row)
                if actual != (x, y):
                    problems.append("%s expected=%s,%s" % (row, x, y))
            s.type(b"q")
            s.finish()
            ctx.common_checks(s, 0, problems)
    path = os.path.join(ctx.ROOT, "target", "pty", "aim-window.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(evidence) + "\n")
    s.evidence = "%d timed sessions; accepted Space/held/aim rows at %s" % (len(evidence), path)
    return s, problems


ROWS = {"held-run": row_held_run, "card": row_card, "title": row_title, "directional-chords": row_directional_chords, "aim-window": row_aim_window}
