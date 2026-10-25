#!/usr/bin/env python3
"""ci/memgate-test.py — the memory gate's decision with both inputs: the
Python `decide` (tools/memgate.py) and the shell `require_memory`
(tools/lib-mem.sh), driven with a stand-in vm_stat. Exit 0 when every case
passes."""
import os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import memgate

fails = 0


def say(ok, what):
    global fails
    print("memgate-test: %s %s" % ("PASS" if ok else "FAIL", what))
    fails += not ok


# The decision: (hostname, lane_host, gate_env, free_gb) -> (applies, ok)
cases = [
    (("nomad", None, None, 3.0), (True, False), "nomad under the floor refuses"),
    (("nomad", None, None, 8.0), (True, True), "nomad at the floor proceeds"),
    (("nomad.local", None, None, 22.1), (True, True), "nomad by a dotted hostname"),
    (("Nomad", None, "1", 7.9), (True, False), "nomad, gate on, just under"),
    (("nomad", None, "0", 1.0), (False, True), "nomad with PACK_MEMORY_GATE=0 is not gated"),
    (("Mac-1234.local", None, None, 3.0), (False, True), "another Mac (GitHub's runner) is not gated"),
    (("Mac-1234.local", "nomad", None, 3.0), (True, False), "PACK_LANE_HOST=nomad gates whatever the hostname"),
    (("hasu", None, None, 0.5), (False, True), "a Linux host is not gated"),
    (("", None, None, 0.0), (False, True), "no hostname at all is not gated"),
]
for args, want, what in cases:
    got = memgate.decide(*args)
    say(got == want, "%s: %r" % (what, got))

# The shell twin, with a stand-in vm_stat on PATH and the hostname by PACK_LANE_HOST.
tmp = tempfile.mkdtemp()
def shell(free_gb, lane_host, gate_env):
    pages = int(free_gb * 1024 ** 3 / 16384)
    with open(os.path.join(tmp, "vm_stat"), "w") as f:
        f.write("#!/bin/sh\nprintf 'Mach Virtual Memory Statistics: (page size of 16384 bytes)\\nPages free: %d.\\nPages inactive: 0.\\nPages speculative: 0.\\n'\n" % pages)
    os.chmod(os.path.join(tmp, "vm_stat"), 0o755)
    with open(os.path.join(tmp, "uname"), "w") as f:
        f.write("#!/bin/sh\ncase \"$1\" in -s) echo Darwin ;; -n) echo other ;; *) echo Darwin ;; esac\n")
    os.chmod(os.path.join(tmp, "uname"), 0o755)
    with open(os.path.join(tmp, "hostname"), "w") as f:
        f.write("#!/bin/sh\necho other\n")
    os.chmod(os.path.join(tmp, "hostname"), 0o755)
    env = {k: v for k, v in os.environ.items() if k not in ("PACK_LANE_HOST", "PACK_MEMORY_GATE")}
    env["PATH"] = tmp + ":" + env.get("PATH", "/usr/bin:/bin")
    if lane_host is not None:
        env["PACK_LANE_HOST"] = lane_host
    if gate_env is not None:
        env["PACK_MEMORY_GATE"] = gate_env
    r = subprocess.run(["sh", "-c", ". '%s/tools/lib-mem.sh'; require_memory; echo proceeded" % ROOT], capture_output=True, text=True, env=env)
    return r.returncode, "proceeded" in r.stdout

rc, went = shell(3.0, "nomad", None)
say(rc == 3 and not went, "shell: nomad under the floor refuses (exit 3)")
rc, went = shell(9.0, "nomad", None)
say(rc == 0 and went, "shell: nomad over the floor proceeds")
rc, went = shell(3.0, "nomad", "0")
say(rc == 0 and went, "shell: PACK_MEMORY_GATE=0 turns the gate off")
rc, went = shell(3.0, None, None)
say(rc == 0 and went, "shell: another host is not gated")

print("memgate-test: %d failure(s)" % fails)
sys.exit(1 if fails else 0)
