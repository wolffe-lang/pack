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
  directional-chords  the decoder (pk06): each held aim typed as simultaneous
              bytes with Space, on both tiers; the one-tick tell's text in
              the live output.
  aim-window  last-key-only autorepeat (pk06b, re-paced by pk09): the first
              arrow, then only the second, then Space 6, 9 or 12 ticks after
              the second starts; every byte written by the game's own trace
              tick and acknowledged on the step that applied it, the Hold
              and aim checked against the documented rule on those applied
              ticks (the block above `row_aim_window` has the protocol).
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


# The aim-window row (pk06b's fixture, re-paced by pk09). Its injections are
# paced by the game's own `--trace` ticks, never by a wall-clock sleep, and
# its verdict is computed from the ticks the game APPLIED, never from the
# milliseconds the row meant: on a shared runner a requested 400 ms gap
# arrived 14-40 ms late and the old row read the game's correct answer to
# the late stream as a fault (pack#44; notes/pk09-the-aim-window.md).
#
# The protocol (cub's cb11/cb11b shape): a trace line `tick N` is printed
# after step N-1, so a byte written once line N is seen is applied on step N
# if the row is in time, later if it is not. Each byte is written alone and
# acknowledged before the next: the first trace line after the write whose
# `keys` is 1 carries it, and its step is the byte's applied tick. A late
# byte is input data, not a failure; a byte never applied, or applied where
# the sim's own record (`<arrow>_at`, `leap_tick`) disagrees, is a DELIVERY
# failure. Requested ticks are pacing targets, not acceptance conditions.
#
# The oracle (`aim_rule`) is the documented rule (docs/KEYS.md, the aimed
# leap; lair's input.lu, the Hold) applied to the acknowledged ticks: an
# arrow counts when held or pressed at most AIM_RULE_WINDOW ticks before
# Space; opposing arrows resolve per axis to the later press. It reads no
# Hold, aim or `_at` field of the game's. The game's raw Hold and aim must
# equal the oracle's in EVERY session.
#
# A diagonal session proves the window only when the stream it realised is
# the case's: the first arrow's Hold over at Space (so the Hold alone cannot
# give the diagonal) and its last press inside the window. A stall can push
# a session out of that class; the session is still checked against the
# oracle, and the case is driven again in a fresh session, up to
# AIM_ATTEMPTS times, every re-drive printed. A case never realised is a
# SCHEDULE failure. No re-drive ever forgives a disagreement.

AIM_ARROWS = {"up": b"\x1b[A", "down": b"\x1b[B", "left": b"\x1b[D", "right": b"\x1b[C"}
AIM_BITS = {"up": 1, "down": 2, "left": 4, "right": 8}

# The documented constants the oracle applies (sim.lu AIM_WINDOW_TICKS;
# lair input.lu HOLD_TAP_TICKS, HOLD_RATE_MAX, HOLD_MARGIN). A change to the
# game's rule is a change to these, in the same commit.
AIM_RULE_WINDOW = 15
HOLD_RULE_TAP = 12
HOLD_RULE_RATE_MAX = 5
HOLD_RULE_MARGIN = 1
# The leap's own preconditions (sim.lu `leap`: LEAP_STAMINA, the pant that
# EXHAUST_RECOVER ends). The row judges the aim, not the sprint, but Up is a
# sprint too: a stall that stretches the first arrow's run can tire the pack
# until the leap is refused, which the game is right to do.
LEAP_RULE_STAMINA = 60
EXHAUST_RULE_RECOVER = 90

# The schedule, in ticks (30 Hz): the first arrow's initial repeat delay
# (~267 ms) and its repeat interval (~67 ms), then the second arrow from the
# tick after the first's last repeat; Space AIM_DELAYS ticks after the
# second arrow starts (200, 300 and 400 ms, the row's three cases).
AIM_START_LINE = 3
AIM_FIRST_DELAY = 8
AIM_REPEAT = 2
AIM_FIRST_REPEATS = 5
AIM_DELAYS = (6, 9, 12)
AIM_ATTEMPTS = 4
# Liveness only: a trace that shows no new tick for this long fails the
# session loudly. It is never a timing bar.
AIM_TRACE_WAIT_S = 20.0


class TraceStall(Exception):
    pass


class NoSession:
    """What the runner keeps when a row stops before its first session."""
    out, err, status = b"", b"", 0

    def __init__(self, evidence):
        self.evidence = evidence


def hold_rule_until(presses):
    """The engine's Hold (lair input.lu `hold_press`) over one key's applied
    press ticks (one per step): the tick the hold ends (held while tick <
    until)."""
    last, prev, until = -1000, -1000, -1
    for t in presses:
        gap, prev_gap = t - last, last - prev
        if gap <= HOLD_RULE_RATE_MAX:
            rate = gap
            if prev_gap <= HOLD_RULE_RATE_MAX and prev_gap > rate:
                rate = prev_gap
            until = t + rate + HOLD_RULE_MARGIN
        elif gap <= HOLD_RULE_TAP + HOLD_RULE_MARGIN:
            until = t + HOLD_RULE_RATE_MAX + HOLD_RULE_MARGIN
        else:
            until = t + HOLD_RULE_TAP
        prev, last = last, t
    return until


def aim_rule(presses, space):
    """The oracle: from each arrow's applied press ticks (in the order the
    row wrote them, each before Space) and Space's tick, the raw Hold mask
    and the aim (x, y) the documented rule gives."""
    held, recent, last = 0, set(), {}
    for name, ticks in presses.items():
        ticks = [t for t in ticks if t <= space]
        if not ticks:
            continue
        until = hold_rule_until(ticks)
        last[name] = ticks[-1]
        if space < until:
            held += AIM_BITS[name]
        if space < until or space - ticks[-1] <= AIM_RULE_WINDOW:
            recent.add(name)

    def axis(pos, neg):
        if pos in recent and neg in recent:
            return 1 if last[pos] > last[neg] else -1
        return 1 if pos in recent else (-1 if neg in recent else 0)

    x, y = axis("right", "left"), axis("up", "down")
    return held, (x, y) if (x, y) != (0, 0) else (0, 1)


def aim_realised(first, second, presses, space):
    """Whether a session's applied stream is its case's: the second arrow
    (the last pressed) inside the window, and for a diagonal the first
    arrow's Hold over at Space (the Hold alone cannot give the diagonal)
    with its last press inside the window too."""
    for name in (first, second):
        if name is None:
            continue
        ticks = [t for t in presses.get(name, []) if t <= space]
        if not ticks or space - ticks[-1] > AIM_RULE_WINDOW:
            return False
        if name == first and space < hold_rule_until(ticks):
            return False
    return True


def leap_rule_ok(rows, space):
    """Whether the documented rule lets a leap start on step `space`, from
    the trace's stamina: the line `tick space` (printed after step space-1)
    holds the stamina the step starts with; the pant began on a line that
    showed 0 and ended on a later line that showed EXHAUST_RULE_RECOVER or
    more. No leap precedes Space in these sessions, so 0 is only the pant."""
    stamina, panting = None, False
    for r in rows:
        if r["tick"] > space:
            break
        stamina = r.get("stamina")
        if stamina == 0:
            panting = True
        elif panting and stamina is not None and stamina >= EXHAUST_RULE_RECOVER:
            panting = False
    return stamina is not None and stamina >= LEAP_RULE_STAMINA and not panting


def first_applied(rows, seen):
    """The acknowledgement: the first trace line at or after index `seen`
    that applied a key -> (its step, the line), or None. The line `tick N`
    is printed after step N-1, so the step is N - 1."""
    for r in rows[seen:]:
        if r.get("keys", 0) >= 1:
            return r["tick"] - 1, r
    return None


class TickPacer:
    """A session driven by its own trace: `line()` is the newest `tick N`
    seen, `press()` writes one key once line N is seen and returns the step
    the game applied it on."""

    def __init__(self, s):
        self.s = s
        self.parsed = 0
        self.partial = b""
        self.rows = []
        self.log = []

    def poll(self, seconds=0.005):
        self.s.pump(seconds)
        fresh = self.s.err[self.parsed:]
        self.parsed = len(self.s.err)
        *lines, self.partial = (self.partial + fresh).split(b"\n")
        self.rows += trace_ticks(b"\n".join(lines))

    def line(self):
        return self.rows[-1]["tick"] if self.rows else 0

    def wait_line(self, n):
        end = time.monotonic() + AIM_TRACE_WAIT_S
        while self.line() < n:
            if time.monotonic() > end:
                raise TraceStall("the trace never reached tick %d (last %d)" % (n, self.line()))
            self.poll()

    def press(self, name, data, step):
        """Write `data` once the step before `step` has run; acknowledge it by
        the first later trace line that applied a key. -> the applied step."""
        self.wait_line(step)
        seen = len(self.rows)
        before = self.line()
        os.write(self.s.master, data)
        end = time.monotonic() + AIM_TRACE_WAIT_S
        while True:
            got = first_applied(self.rows, seen)
            if got:
                applied, r = got
                self.log.append((name, step, before, applied, r))
                return applied
            if time.monotonic() > end:
                raise TraceStall("%s written after line %d was never applied (last line %d)" % (name, before, self.line()))
            self.poll()


def aim_session(bin, ctx, tier, first, second, delay):
    """One fresh session of one case: the paced stream, the acknowledgement
    of every byte, the game's answer and the oracle's. -> (session, record,
    problems)."""
    s = ctx.Session([bin, "--seed", "7", "--tier", tier, "--trace", "--no-title"], 24, 80, ctx.env_for())
    p = TickPacer(s)
    problems = []
    presses = {}
    rec = {"tier": tier, "first": first, "second": second, "delay": delay}
    try:
        p.wait_line(AIM_START_LINE)
        second_from = p.line()
        if first:
            t = p.press(first, AIM_ARROWS[first], p.line())
            presses[first] = [t]
            for n in range(AIM_FIRST_REPEATS):
                t = p.press(first, AIM_ARROWS[first], t + (AIM_FIRST_DELAY if n == 0 else AIM_REPEAT))
                presses[first].append(t)
            second_from = t + 1
        space_at = second_from + delay
        if second:
            t = p.press(second, AIM_ARROWS[second], second_from)
            presses[second] = [t]
            while t + AIM_REPEAT < space_at:
                t = p.press(second, AIM_ARROWS[second], t + AIM_REPEAT)
                presses[second].append(t)
        space = p.press("space", b" ", space_at)
        p.wait_line(space + 4)
    except TraceStall as e:
        problems.append("%s %s>%s delay=%d: DELIVERY: %s" % (tier, first, second, delay, e))
        s.type(b"q")
        s.finish()
        return s, rec, problems
    s.type(b"q")
    s.finish()
    ctx.common_checks(s, 0, problems)
    tag = "%s %s>%s delay=%d" % (tier, first, second, delay)
    # Delivery: the sim's own record of each acknowledged arrow.
    for name, step, before, applied, r in p.log:
        if name != "space" and r.get(name + "_at") != applied:
            problems.append("%s: DELIVERY: %s applied on step %d but the trace says %s_at %s" % (
                tag, name, applied, name, r.get(name + "_at")))
    tells = [r for r in p.rows if r.get("tell") == 1]
    leap_ok = leap_rule_ok(p.rows, space)
    late = sum(applied - step for name, step, before, applied, r in p.log)
    rec.update({"space": space, "presses": presses, "late": late, "leap_ok": leap_ok,
                "first_gap": space - presses[first][-1] if first else None,
                "second_gap": space - presses[second][-1] if second else None})
    if not leap_ok:
        # The stream tired the pack: no leap is the rule's answer, and the
        # session is out of its case.
        if tells:
            problems.append("%s: the game leapt on step %s where its stamina rule refuses (Space %d)" % (
                tag, [r.get("leap_tick") for r in tells], space))
        rec.update({"realised": False, "held": None, "aim": None, "rule_held": None, "rule_aim": None})
        return s, rec, problems
    if len(tells) != 1 or tells[0].get("leap_tick") != space:
        problems.append("%s: one leap on Space's step %d wanted, the trace has %r" % (
            tag, space, [(r.get("tick"), r.get("leap_tick")) for r in tells]))
    acc = tells[-1] if tells else {}
    rule_held, rule_aim = aim_rule(presses, space)
    game_held, game_aim = acc.get("leap_held"), (acc.get("aim_x"), acc.get("aim_y"))
    rec.update({"rule_held": rule_held, "rule_aim": rule_aim, "held": game_held, "aim": game_aim,
                "realised": aim_realised(first, second, presses, space)})
    if game_held != rule_held:
        problems.append("%s: the game's Hold at Space is %s where the rule on the applied ticks gives %s (presses %s, Space %d)" % (
            tag, game_held, rule_held, presses, space))
    if game_aim != rule_aim:
        problems.append("%s: the game aims %s,%s where the rule on the applied ticks gives %s,%s (presses %s, Space %d)" % (
            tag, game_aim[0], game_aim[1], rule_aim[0], rule_aim[1], presses, space))
    return s, rec, problems


def aim_controls():
    """The oracle's own rows: the documented rule on hand-made ticks, and the
    pacer's acknowledgement on a hand-made trace. -> failures."""
    bad = []

    def want(name, got, expected):
        if got != expected:
            bad.append("%s: %r, wanted %r" % (name, got, expected))

    want("a lone press holds 12", hold_rule_until([10]), 22)
    want("2-tick repeats hold 3 past the last", hold_rule_until([10, 18, 20, 22]), 25)
    want("1-tick repeats hold 2 past the last", hold_rule_until([10, 11, 12]), 14)
    want("the larger of the last two gaps", hold_rule_until([10, 12, 13]), 16)
    want("a 6-tick gap is a fresh delay", hold_rule_until([10, 16]), 22)
    want("a 14-tick gap is a fresh tap", hold_rule_until([10, 24]), 36)
    up = [10, 18, 20, 22, 24, 26]
    want("NE inside the window", aim_rule({"up": up, "right": [27, 29, 31, 33, 35, 37]}, 39), (8, (1, 1)))
    want("the window's edge, 15 ticks", aim_rule({"up": up, "right": [27, 29, 31, 33, 35, 37, 39]}, 41), (8, (1, 1)))
    want("expired at 16 ticks", aim_rule({"up": up, "right": [27, 29, 31, 33, 35, 37, 39]}, 42), (0, (1, 0)))
    want("the first still held", aim_rule({"up": up, "right": [27]}, 28), (9, (1, 1)))
    want("cardinal alone", aim_rule({"left": [10, 12, 14]}, 15), (4, (-1, 0)))
    want("the default", aim_rule({}, 20), (0, (0, 1)))
    want("opposing: the later wins", aim_rule({"left": [10], "right": [12]}, 14), (12, (1, 0)))
    want("opposing reversed", aim_rule({"right": [10], "left": [12]}, 14), (12, (-1, 0)))
    want("an arrow after Space never counts", aim_rule({"up": [10], "right": [21]}, 20), (1, (0, 1)))
    right = [27, 29, 31, 33, 35, 37]
    want("realised", aim_realised("up", "right", {"up": up, "right": right}, 39), True)
    want("unrealised past the window", aim_realised("up", "right", {"up": up, "right": right}, 42), False)
    want("unrealised while the first is held", aim_realised("up", "right", {"up": [10, 24], "right": [25]}, 30), False)
    want("a cardinal inside the window", aim_realised(None, "left", {"left": [10]}, 25), True)
    want("a cardinal past it", aim_realised(None, "left", {"left": [10]}, 26), False)
    want("the default", aim_realised(None, None, {}, 20), True)
    def lines(*stamina):
        return [{"tick": t + 1, "stamina": v} for t, v in enumerate(stamina)]

    want("a fresh pack leaps", leap_rule_ok(lines(300, 294, 288), 3), True)
    want("60 is enough", leap_rule_ok(lines(300, 66, 60), 3), True)
    want("59 is not", leap_rule_ok(lines(300, 65, 59), 3), False)
    want("the pant refuses", leap_rule_ok(lines(6, 0, 1, 2), 4), False)
    want("the pant past 89 still refuses", leap_rule_ok(lines(0, 88, 89), 3), False)
    want("the pant ends at 90", leap_rule_ok(lines(0, 89, 90), 3), True)
    want("lines after Space never count", leap_rule_ok(lines(300, 300, 0, 0), 2), True)

    # The second key dropped (the plant's fault) must not agree with the rule.
    if aim_rule({"up": up, "right": [27, 29]}, 31)[1] == (0, 1):
        bad.append("the rule cannot tell a dropped second key from the diagonal")

    # The acknowledgement: a key line before the write is never ours; the
    # first key line after it is, at its step (line - 1).
    class Fake:
        master = None

        def __init__(self):
            self.err = b""

        def pump(self, seconds):
            pass

    f = Fake()
    p = TickPacer(f)
    f.err = b"trace tick 5 in 0 keys 0\ntrace tick 6 in 3 keys 1\ntrace tick 7 in 0 keys 0\n"
    p.poll()
    want("the newest line", p.line(), 7)
    seen = len(p.rows)
    want("nothing acknowledged before the line", first_applied(p.rows, seen), None)
    f.err += b"trace tick 8 in 0 keys 0\ntrace tick 9 in 3 keys 1 up_at 8\ntrace tick 10 in 0 keys 0\ntrace tick"
    p.poll()
    got = first_applied(p.rows, seen)
    want("the acknowledgement is step 8, not the earlier key line", got and got[0], 8)
    want("a partial line waits", p.line(), 10)
    f.err += b" 11 in 0 keys 0\n"
    p.poll()
    want("and is read once complete", p.line(), 11)
    return bad


def row_aim_window(bin, ctx):
    """One key repeats at a time: the first arrow, then only the second, Space;
    paced by the game's ticks and judged on the ticks it applied."""
    problems = ["oracle control: " + b for b in aim_controls()]
    if problems:
        return NoSession("the oracle's controls failed; no session run"), problems
    cases = [("up", "right", 1, 1), ("right", "up", 1, 1),
             ("up", "left", -1, 1), ("left", "up", -1, 1),
             ("down", "right", 1, -1), ("right", "down", 1, -1),
             ("down", "left", -1, -1), ("left", "down", -1, -1)]
    cases = [(a, b, x, y, d) for a, b, x, y in cases for d in AIM_DELAYS]
    cases += [(None, name, x, y, AIM_DELAYS[1]) for name, x, y in
              [("up", 0, 1), ("down", 0, -1), ("left", -1, 0), ("right", 1, 0)]]
    cases += [(None, None, 0, 1, AIM_DELAYS[1])]
    evidence, s, sessions, redriven, late = [], None, 0, 0, 0
    for tier in ("rich", "plain"):
        for first, second, x, y, delay in cases:
            for attempt in range(1, AIM_ATTEMPTS + 1):
                s, rec, found = aim_session(bin, ctx, tier, first, second, delay)
                sessions += 1
                problems += found
                if "space" not in rec:
                    break
                late += rec["late"]
                evidence.append("%s %s>%s delay=%d attempt=%d presses=%s Space=%d first_gap=%s second_gap=%s "
                                "late=%d leap_ok=%s held=%s rule_held=%s aim=%s rule_aim=%s realised=%s" % (
                                    tier, first, second, delay, attempt, rec["presses"], rec["space"],
                                    rec["first_gap"], rec["second_gap"], rec["late"], rec["leap_ok"], rec["held"],
                                    rec["rule_held"], rec["aim"], rec["rule_aim"], rec["realised"]))
                if found or rec["realised"]:
                    if not found and rec["rule_aim"] != (x, y):
                        problems.append("%s %s>%s delay=%d: realised, but the rule gives %s where the case is %s,%s" % (
                            tier, first, second, delay, rec["rule_aim"], x, y))
                    break
                redriven += 1
                evidence.append("  re-driven: the applied stream left the case (%s)" % (
                    "the pack too tired to leap" if not rec["leap_ok"] else "first_gap %s, Space %d" % (rec["first_gap"], rec["space"])))
            else:
                problems.append("%s %s>%s delay=%d: SCHEDULE: not realised in %d sessions" % (
                    tier, first, second, delay, AIM_ATTEMPTS))
    path = os.path.join(ctx.ROOT, "target", "pty", "aim-window.txt")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(evidence) + "\n")
    s.evidence = "%d cases in %d tick-paced sessions (%d re-driven, %d ticks of late delivery); rows at %s" % (
        len(cases) * 2, sessions, redriven, late, path)
    return s, problems


ROWS = {"held-run": row_held_run, "card": row_card, "title": row_title, "directional-chords": row_directional_chords, "aim-window": row_aim_window}


if __name__ == "__main__":
    # `python3 -I tests/pty_rows.py`: the aim-window oracle's controls alone
    # (the row runs them before its first session too).
    import sys
    bad = aim_controls()
    for b in bad:
        print("aim-window control FAILED: " + b)
    print("aim-window controls: %s" % ("FAILED" if bad else "ok"))
    sys.exit(1 if bad else 0)
