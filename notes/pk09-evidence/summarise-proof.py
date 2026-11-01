#!/usr/bin/env python3
"""notes/pk09-evidence/summarise-proof.py DIR — the proof's table from its
logs alone (proof.sh's `<label>-<k>.log` and `<label>-<k>-sessions.txt`).

For trunk's runs: each red line by class (`fixture Hold set`, `expected=`,
`accepted Space rows`), and the aim the documented window gives on the
ticks each session's trace reported (an arrow counts when its last press
is at most 15 ticks before Space; the Hold ends within 12, so the window
decides), against the aim the game chose: a disagreement would be an aim
fault, and the table counts them.
For the head's runs: the verdict line, sessions, re-drives, late ticks, and
every session's game Hold and aim against the rule's.
"""
import glob, os, re, sys

WINDOW = 15


def trunk_rule_aim(row):
    m = dict(re.findall(r"(\w+_at)=(-?\d+)", row))
    space = int(re.search(r"Space=(\d+)", row).group(1))
    recent = {k[:-3] for k, v in m.items() if int(v) > -1000 and space - int(v) <= WINDOW}
    x = (1 if "right" in recent else 0) - (1 if "left" in recent else 0)
    y = (1 if "up" in recent else 0) - (1 if "down" in recent else 0)
    return (x, y) if (x, y) != (0, 0) else (0, 1)


def main(d):
    out = []
    for label in ("trunk", "head"):
        logs = sorted(glob.glob(os.path.join(d, "%s-[0-9]*.log" % label)))
        green = red = 0
        classes = {}
        disagree = sessions = redriven = late = mismatched = 0
        for log in logs:
            text = open(log, encoding="utf-8", errors="replace").read()
            k = re.search(r"-(\d+)\.log$", log).group(1)
            ok = re.search(r"^pty: aim-window ok", text, re.M)
            bad = re.search(r"^pty: aim-window FAILED", text, re.M)
            green += bool(ok)
            red += bool(bad)
            lines = re.findall(r"^  - (.*)$", text, re.M)
            for l in lines:
                c = ("fixture Hold set" if "fixture Hold set" in l else "expected=" if "expected=" in l
                     else "accepted Space rows" if "accepted Space rows" in l else "other")
                classes[c] = classes.get(c, 0) + 1
            rows_path = os.path.join(d, "%s-%s-sessions.txt" % (label, k))
            # A run without a verdict never ran its sessions; the file beside
            # it is a stale copy of the run before, so it is not read.
            rows = open(rows_path, encoding="utf-8").read().splitlines() if (ok or bad) and os.path.exists(rows_path) else []
            if label == "trunk":
                for r in rows:
                    if "Space=" not in r:
                        continue
                    sessions += 1
                    aim = tuple(int(v) for v in re.search(r"aim=(-?\d+),(-?\d+)", r).groups())
                    if aim != trunk_rule_aim(r):
                        disagree += 1
                out.append("%s run %s: %s, %d lines" % (label, k, "green" if ok else "RED" if bad else "NO VERDICT", len(lines)))
            else:
                for r in rows:
                    if r.startswith("  re-driven"):
                        redriven += 1
                        continue
                    if "Space=" not in r:
                        continue
                    sessions += 1
                    late += int(re.search(r"late=(\d+)", r).group(1))
                    g = re.search(r"held=(\S+) rule_held=(\S+) aim=(.*?) rule_aim=(.*?) realised", r)
                    if g and (g.group(1) != g.group(2) or g.group(3) != g.group(4)):
                        mismatched += 1
                verdict = re.search(r"^pty: aim-window .*$", text, re.M)
                out.append("%s run %s: %s" % (label, k, verdict.group(0)[:200] if verdict else "NO VERDICT"))
        if label == "trunk":
            out.append("SUMMARY trunk: %d green, %d red, %d without a verdict, of %d; red lines by class %s; %d sessions, the game's "
                       "aim against the window on its own reported ticks: %d disagree" % (
                           green, red, len(logs) - green - red, len(logs), classes, sessions, disagree))
        else:
            out.append("SUMMARY head: %d green, %d red, %d without a verdict, of %d; %d sessions, %d re-driven, %d ticks of late "
                       "delivery, %d where the game's Hold or aim differs from the rule's; red lines %s" % (
                           green, red, len(logs) - green - red, len(logs), sessions, redriven, late, mismatched, classes))
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
