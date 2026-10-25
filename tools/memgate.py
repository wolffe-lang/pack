"""tools/memgate.py — RULES section 4's memory gate, as one decision.

The gate is nomad's rule (the maintainer's Mac, where an MLX server holds
15 to 30 GB): a heavy job runs only with 8 GB free, inactive and
speculative together, read from vm_stat by the script itself. It is not a
rule for any other host: GitHub's macOS runner reads a small free figure
that means nothing for it, and Linux hosts have blocks and --memory. So
the gate APPLIES only when the host is nomad (its hostname, or
PACK_LANE_HOST=nomad for a lane script that knows) and PACK_MEMORY_GATE is
not 0 (the workflow's macOS job sets 0). `decide` is the pure function
tools/pty, tools/perf-idle and tools/lib-mem.sh implement, tested by
ci/memgate-test.py with both inputs.
"""
import os, re, socket, subprocess, sys

FLOOR_GB = 8


def applies(hostname, lane_host, gate_env):
    """Whether the gate applies at all: nomad (by hostname or by the lane's
    word), unless PACK_MEMORY_GATE is 0."""
    if gate_env is not None and gate_env.strip() == "0":
        return False
    host = (lane_host or hostname or "").split(".")[0].lower()
    return host == "nomad"


def decide(hostname, lane_host, gate_env, free_gb):
    """-> (applies, ok): ok is True when the gate does not apply or the free
    memory is at least the floor."""
    if not applies(hostname, lane_host, gate_env):
        return False, True
    return True, free_gb >= FLOOR_GB


def free_gb_darwin():
    out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
    page = int(re.search(r"page size of (\d+) bytes", out).group(1))
    pages = 0
    for key in ("Pages free", "Pages inactive", "Pages speculative"):
        m = re.search(key + r":\s+(\d+)", out)
        pages += int(m.group(1)) if m else 0
    return pages * page / 1024 ** 3


def check(tool):
    """The gate for a running tool: True to proceed. Prints the refusal."""
    if sys.platform != "darwin":
        return True
    free = free_gb_darwin()
    applied, ok = decide(socket.gethostname(), os.environ.get("PACK_LANE_HOST"), os.environ.get("PACK_MEMORY_GATE"), free)
    if applied and not ok:
        print("%s: REFUSED on nomad: %.1f GB free+inactive+speculative, the floor is %d GB (RULES section 4)" % (tool, free, FLOOR_GB))
    return ok
