#!/usr/bin/env python3
"""ci/tiers-test.py — the planner's own proof (clef's T1-T8, cut to pack's
jobs). python3 only.

  T1  the tiers by event: a trunk push, the nightly, a dispatch with no
      jobs and the `full-matrix` label are full; another label's
      `labeled` event is a noop; a dispatch naming jobs is partial, and
      refuses a job the workflow does not have.
  T2  the pull-request tiers by path: code is pr (plan-test, linux); prose
      alone is noop; prose beside code is pr.
  T3  full wins: a path no rule names; changed paths that cannot be read.
  T4  the wiring of .github/workflows/ci.yml: every job but `plan` needs
      it and runs only when the plan names it; `tier` needs every job,
      runs on `!cancelled()` and calls the verdict; cancel-in-progress is
      for pull requests only; the trunk push, the nightly, the label and
      the dispatch input are there; macos and perf are no pull-request job.
  T6  the verdict: green for a full, a pr, a noop and a partial run; red
      for a chosen job failed or skipped, a job that ran unasked, a failed
      plan, a plan with no tier, a full that chose less.
  T8  ci/nightly-red.sh against a stand-in `gh`: no open issue opens one;
      an open one is commented on; a label that exists is no failure; the
      script refuses without its environment; the nightly-red job runs on
      a failed schedule only, after the verdict.

Exit 0 when every check passes, 1 otherwise.
"""
import json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = os.path.join(ROOT, "ci", "tiers.py")
WF = open(os.path.join(ROOT, ".github", "workflows", "ci.yml"), encoding="utf-8").read()
KEYS = ("EVENT", "ACTION", "LABEL", "LABELS", "HEAD_SHA", "IN_JOBS", "NEEDS")
fails = 0
ALL = ["plan-test", "linux", "macos", "perf"]
PR = ["plan-test", "linux"]


def say(ok, what):
    global fails
    print("tiers-test: %s %s" % ("PASS" if ok else "FAIL", what))
    fails += not ok


def env(**more):
    e = {k: v for k, v in os.environ.items() if k not in KEYS}
    e.update(more)
    return e


def plan(paths=None, **kw):
    args = [sys.executable, PLAN, "plan", "--json"]
    for k, v in kw.items():
        args += ["--" + k.replace("_", "-"), v]
    if paths is not None:
        args += ["--paths-from", "-"]
    r = subprocess.run(args, input="\n".join(paths or []) + "\n", capture_output=True, text=True, env=env())
    if r.returncode != 0:
        return {"tier": "ERROR %d" % r.returncode, "jobs": []}
    return json.loads(r.stdout)


def verdict(needs):
    r = subprocess.run([sys.executable, PLAN, "verdict"], capture_output=True, text=True,
                       env=env(NEEDS=json.dumps(needs)))
    return r.returncode


def needs_for(tier, chosen, results=None):
    n = {"plan": {"result": "success", "outputs": {"tier": tier, "jobs": json.dumps(chosen)}}}
    for j in ALL:
        n[j] = {"result": (results or {}).get(j, "success" if j in chosen else "skipped")}
    return n


# T1
for ev in ("push", "schedule", "workflow_dispatch"):
    p = plan(event=ev)
    say(p["tier"] == "full" and p["jobs"] == ALL, "T1 %s is full" % ev)
p = plan(["src/pack.lu"], event="pull_request", action="labeled", label="full-matrix", labels="full-matrix")
say(p["tier"] == "full" and p["jobs"] == ALL, "T1 the full-matrix label is full")
p = plan(["src/pack.lu"], event="pull_request", action="labeled", label="bug")
say(p["tier"] == "noop" and p["jobs"] == [], "T1 another label is a noop")
p = plan(event="workflow_dispatch", jobs="plan-test linux")
say(p["tier"] == "partial" and p["jobs"] == ["plan-test", "linux"], "T1 a dispatch naming jobs is partial")
p = plan(event="workflow_dispatch", jobs="windows")
say(p["tier"].startswith("ERROR"), "T1 a dispatch naming an unknown job is refused")

# T2
p = plan(["src/grid/grid.lu"], event="pull_request", action="synchronize")
say(p["tier"] == "pr" and p["jobs"] == PR, "T2 code is pr")
p = plan(["README.md", "docs/ART.md", "notes/pk00-the-engine.md"], event="pull_request", action="opened")
say(p["tier"] == "noop" and p["jobs"] == [], "T2 prose alone is noop")
p = plan(["docs/ART.md", "tools/pty"], event="pull_request", action="opened")
say(p["tier"] == "pr", "T2 prose beside code is pr")
for path, want in (("tests/goldens/trot-rich/final.txt", "pr"), ("wolf-toolchain.toml", "pr"), (".github/workflows/ci.yml", "pr"), ("ci/tiers.py", "pr")):
    p = plan([path], event="pull_request", action="opened")
    say(p["tier"] == want, "T2 %s is %s" % (path, want))

# T3
p = plan(["Makefile"], event="pull_request", action="opened")
say(p["tier"] == "full", "T3 a path no rule names is full")
p = plan(event="pull_request", action="opened")
say(p["tier"] == "full", "T3 unreadable paths are full")
p = plan([], event="pull_request", action="opened")
say(p["tier"] == "full", "T3 no paths is full")

# T4
jobs_section = WF.split("\njobs:\n", 1)[1]
jobs = re.findall(r"^  ([a-z-]+):\s*$", jobs_section, re.M)
say(set(jobs) == set(ALL + ["plan", "tier", "nightly-red"]), "T4 the workflow's jobs are the planner's (%s)" % " ".join(jobs))


def job_body(name):
    m = re.search(r"\n  %s:\n(.*?)(?=\n  [a-z-]+:\n|\Z)" % re.escape(name), jobs_section, re.S)
    return m.group(1) if m else ""


for j in ALL:
    body = job_body(j)
    say("needs: plan" in body and "contains(fromJSON(needs.plan.outputs.jobs || '[]'), '%s')" % j in body, "T4 %s needs the plan and runs when named" % j)
tier_body = job_body("tier")
say(all(("- %s" % j) in tier_body for j in ["plan"] + ALL), "T4 tier needs every job")
say("!cancelled()" in tier_body and "ci/tiers.py verdict" in tier_body, "T4 tier runs on !cancelled() and calls the verdict")
say("cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in WF, "T4 cancel-in-progress for pull requests only")
say("branches: [trunk]" in WF and "schedule:" in WF and "labeled" in WF and "jobs:\n        description" in WF, "T4 the trunk push, the nightly, the label and the dispatch input")
say("macos" not in PR and "perf" not in PR, "T4 macos and perf are no pull-request job")
say("macos-latest" in job_body("macos"), "T4 macos runs on a macOS runner")
say("failure() && github.event_name == 'schedule'" in job_body("nightly-red") and "needs: tier" in job_body("nightly-red"), "T4 nightly-red runs on a failed schedule after the verdict")

# T6
say(verdict(needs_for("full", ALL)) == 0, "T6 a green full run")
say(verdict(needs_for("pr", PR)) == 0, "T6 a green pr run")
say(verdict(needs_for("noop", [])) == 0, "T6 a green noop run")
say(verdict(needs_for("partial", ["plan-test"])) == 0, "T6 a green partial run")
say(verdict(needs_for("pr", PR, {"linux": "failure"})) == 1, "T6 a chosen job failed is red")
say(verdict(needs_for("pr", PR, {"linux": "skipped"})) == 1, "T6 a chosen job skipped is red")
say(verdict(needs_for("pr", PR, {"macos": "success"})) == 1, "T6 a job that ran unasked is red")
n = needs_for("pr", PR); n["plan"]["result"] = "failure"
say(verdict(n) == 1, "T6 a failed plan is red")
n = needs_for("pr", PR); n["plan"]["outputs"]["tier"] = ""
say(verdict(n) == 1, "T6 a plan with no tier is red")
say(verdict(needs_for("full", PR)) == 1, "T6 a full that chose less is red")

# T8
tmp = tempfile.mkdtemp()
log = os.path.join(tmp, "gh.log")
gh = os.path.join(tmp, "gh")
with open(gh, "w") as f:
    f.write("#!/bin/sh\necho \"$@\" >> '%s'\ncase \"$1 $2\" in\n'issue list') echo \"${GH_OPEN:-}\" ;;\n'label create') exit ${GH_LABEL_EXIT:-0} ;;\nesac\n" % log)
os.chmod(gh, 0o755)
script = os.path.join(ROOT, "ci", "nightly-red.sh")


def run_red(gh_open="", label_exit="0", with_env=True):
    if os.path.exists(log):
        os.remove(log)
    e = env(PATH=tmp + ":" + os.environ["PATH"], GH_OPEN=gh_open, GH_LABEL_EXIT=label_exit)
    if with_env:
        e.update(REPO="wolffe-lang/pack", WORKFLOW="ci", RUN_URL="https://example.invalid/run/1", GH_TOKEN="x")
    r = subprocess.run(["bash", script], capture_output=True, text=True, env=e)
    calls = open(log).read() if os.path.exists(log) else ""
    return r.returncode, calls


rc, calls = run_red()
say(rc == 0 and "issue create" in calls and "issue comment" not in calls, "T8 no open issue: one is opened")
rc, calls = run_red(gh_open="42")
say(rc == 0 and "issue comment 42" in calls and "issue create" not in calls, "T8 an open issue is commented on")
rc, calls = run_red(label_exit="1")
say(rc == 0 and "issue create" in calls, "T8 a label that exists is no failure")
rc, calls = run_red(with_env=False)
say(rc != 0, "T8 the script refuses without its environment")
shutil.rmtree(tmp)

print("tiers-test: %d failure(s)" % fails)
sys.exit(1 if fails else 0)
