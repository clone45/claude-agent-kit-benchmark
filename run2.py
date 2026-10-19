#!/usr/bin/env python3
"""Generalized runner: fresh sessions and chained sessions, shell-command checks, any repo.

usage: run2.py --config config2.json --tasks all --conditions A,B --modes fresh,chain --reps 2 [--dry-run]

fresh: each task in its own session from its own base branch (as in phase one).
chain: all selected tasks in chain order inside ONE continued session per condition and repetition,
       starting from the chain base branch; the harness commits a checkpoint after every task so each
       task's diff and checks are isolated, and the next task continues from that state.
`--reps N` is a target per cell; completed runs count toward it.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import pathlib
import random
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
import metrics  # noqa: E402

RATE_LIMIT_RE = re.compile(r"rate.?limit|usage limit|limit reached|too many requests|hit your (session|weekly|opus|sonnet)|overloaded", re.I)


def load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def escaped_project_dir(path):
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def sh(cmd, cwd=None, timeout=None, env=None, shell=False):
    try:
        r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout, env=env, shell=shell)
        return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as e:
        so = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        se = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        return {"rc": None, "stdout": so, "stderr": se, "timed_out": True}


class Repo:
    def __init__(self, config):
        self.dir = config["repo_dir"]
        self.keep = config.get("clean_keep", [])

    def git(self, *args, check=True):
        r = sh(["git", *args], cwd=self.dir)
        if check and r["rc"] != 0:
            raise SystemExit(f"git {' '.join(args)} failed: {r['stderr']}")
        return r["stdout"]

    def clean(self, keep=True):
        args = []
        for k in (self.keep if keep else []):
            args += ["-e", k]
        self.git("clean", "-qfdx", *args)

    def reset_to(self, ref, wipe_scratch):
        self.git("checkout", "-q", "-f", ref)
        self.git("reset", "-q", "--hard")
        self.clean(keep=not wipe_scratch)
        if wipe_scratch:
            shutil.rmtree(pathlib.Path(self.dir) / ".claude", ignore_errors=True)
        status = self.git("status", "--porcelain").strip()
        if status:
            raise SystemExit(f"repo not clean after reset:\n{status}")
        return self.git("rev-parse", "HEAD").strip()

    def head(self):
        return self.git("rev-parse", "HEAD").strip()

    def checkpoint(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.head()

    def diff(self, a, b):
        return self.git("diff", a, b), self.git("diff", "--stat", a, b) + "\n" + self.git("diff", "--name-status", a, b)

    def restore(self, commit):
        self.git("reset", "-q", "--hard", commit)
        self.clean(keep=True)


def clear_auto_memory(config):
    proj = pathlib.Path.home() / ".claude" / "projects" / escaped_project_dir(config["repo_dir"])
    shutil.rmtree(proj / "memory", ignore_errors=True)
    return proj


def build_command(config, task, cond, prompt, session_id, resume):
    budget = config["max_budget_usd"][task["length"]]
    cmd = [config["claude_bin"], "-p", prompt, "--model", config["model"], "--effort", config["effort"],
           "--permission-mode", config["permission_mode"], "--setting-sources", "project,local", "--strict-mcp-config",
           "--output-format", "stream-json", "--verbose", "--forward-subagent-text", "--include-hook-events",
           "--max-budget-usd", str(budget)]
    cmd += ["--resume", session_id] if resume else ["--session-id", session_id]
    if cond["plugin"]:
        cmd += ["--plugin-dir", config["plugin_dir"]]
    return cmd


def run_claude(cmd, cwd, timeout, out_dir):
    env = dict(os.environ)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SSE_PORT"):
        env.pop(k, None)
    started = time.time()
    with open(out_dir / "stream.jsonl", "w", encoding="utf-8") as so, open(out_dir / "stderr.txt", "w", encoding="utf-8") as se:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=so, stderr=se, text=True)
        timed_out = False
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.send_signal(signal.SIGINT)
            try:
                rc = proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:
                    rc = proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    rc = proc.wait()
    return {"rc": rc, "wall_s": round(time.time() - started, 1), "timed_out": timed_out,
            "started_at": dt.datetime.fromtimestamp(started, dt.timezone.utc).isoformat(), "ended_at": now_iso()}


def copy_transcripts(proj_dir, session_id, out_dir):
    tdir = out_dir / "transcript"
    tdir.mkdir(exist_ok=True)
    time.sleep(2)
    found = {"main": False, "subagents": 0}
    main = proj_dir / f"{session_id}.jsonl"
    if main.exists():
        shutil.copyfile(main, tdir / "main.jsonl")
        found["main"] = True
    sub = proj_dir / session_id / "subagents"
    if sub.exists():
        shutil.copytree(sub, tdir / "subagents", dirs_exist_ok=True)
        found["subagents"] = len(list(sub.glob("agent-*.jsonl")))
    return found


def cpp_function_length(path, name):
    try:
        lines = pathlib.Path(path).read_text(encoding="utf-8", errors="replace").split("\n")
    except OSError:
        return None
    pat = re.compile(r"^\s*[\w:<>&\s\*]*\b" + re.escape(name) + r"\s*\(")
    for i, line in enumerate(lines):
        if pat.match(line) and not line.strip().endswith(";"):
            depth = 0
            seen = False
            for j in range(i, len(lines)):
                depth += lines[j].count("{") - lines[j].count("}")
                if "{" in lines[j]:
                    seen = True
                if seen and depth <= 0:
                    return j - i + 1
    return None


def run_checks(config, task, repo, out_dir, diff_text):
    cdir = out_dir / "checks"
    cdir.mkdir(exist_ok=True)
    timeout = config["timeouts_s"]["check"]
    results = {}
    if task.get("hidden_tests"):
        hidden_root = HERE / config["hidden_root"] / task["id"]
        for rel in task["hidden_tests"]:
            dest = pathlib.Path(repo.dir) / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(hidden_root / rel, dest)
    for chk in task["checks"]:
        name = chk["name"]
        if chk.get("internal"):
            if name == "no_changes":
                results[name] = {"pass": diff_text.strip() == "", "diff_bytes": len(diff_text)}
            elif name == "process_length":
                lens = {f"{rel}:{fn}": cpp_function_length(pathlib.Path(repo.dir) / rel, fn) for rel, fn in task.get("function_metrics", [])}
                results["function_lengths"] = lens
            continue
        r = sh(["bash", "-c", chk["cmd"]], cwd=repo.dir, timeout=timeout)
        (cdir / f"{name}.txt").write_text(f"$ {chk['cmd']}\nrc={r['rc']} timed_out={r['timed_out']}\n--- stdout\n{r['stdout']}\n--- stderr\n{r['stderr']}", encoding="utf-8")
        tail = (r["stdout"].strip().splitlines() or [""])[-1]
        results[name] = {"pass": r["rc"] == 0, "rc": r["rc"], "timed_out": r["timed_out"], "tail": tail[:300]}
    gate = [k for k, v in results.items() if isinstance(v, dict) and "pass" in v]
    results["all_pass"] = all(results[k]["pass"] for k in gate) if gate else None
    return results


def detect_rate_limit(result, stderr_text, ss):
    texts = []
    if result:
        texts.append(str(result.get("result", "")))
        texts.extend(str(x) for x in (result.get("errors") or []))
        if result.get("api_error_status") == 429:
            return True
    texts.append(stderr_text[-4000:])
    if "rate_limit" in ss.get("api_retry_errors", []) and (result is None or result.get("is_error")):
        return True
    return any(RATE_LIMIT_RE.search(t) for t in texts if t) and (result is None or result.get("is_error"))


def usage_delta(current, previous):
    """Per-model difference of cumulative modelUsage; None fields if not cumulative."""
    if not current:
        return None, False
    if not previous:
        return current, True
    out = {}
    cumulative = True
    keys = ("inputTokens", "outputTokens", "cacheReadInputTokens", "cacheCreationInputTokens", "thinkingTokens", "costUSD")
    for model, mu in current.items():
        prev = previous.get(model) or {}
        d = dict(mu)
        for k in keys:
            if isinstance(mu.get(k), (int, float)):
                d[k] = mu[k] - (prev.get(k) or 0)
                if d[k] < -1e-9:
                    cumulative = False
        out[model] = d
    return (out if cumulative else current), cumulative


def existing_completed(results_dir, task_id, cond_id, mode_label):
    n = 0
    for rj in results_dir.glob("*/run.json"):
        try:
            d = load_json(rj)
        except json.JSONDecodeError:
            continue
        if d.get("task_id") == task_id and d.get("condition_id") == cond_id and d.get("session_mode") == mode_label and d.get("status") == "completed":
            n += 1
    return n


def append_mapping(config, blind_id, info):
    p = HERE / config["mapping_file"]
    m = load_json(p) if p.exists() else {}
    m[blind_id] = info
    p.write_text(json.dumps(m, indent=2), encoding="utf-8")


def append_grading_row(config, blind_id, task):
    p = HERE / config["grading_sheet"]
    new = not p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["blind_id", "task", "type", "score_1_to_5", "notes"])
        w.writerow([blind_id, task["label"], task["type"], "", ""])


def one_run(config, prices, repo, task, cond, mode, rep_index, results_dir, dry_run, chain=None):
    """chain: dict(session_id, chain_id, step, prev_checkpoint, prev_usage, started) or None for fresh."""
    run_id = str(uuid.uuid4())
    blind_id = str(uuid.uuid4())
    out_dir = results_dir / run_id
    if chain is None:
        session_id = str(uuid.uuid4())
        branch = task["branches"][cond["id"]]["branch"]
        prompt = task["prompt"]
        resume = False
    else:
        session_id = chain["session_id"]
        branch = None
        prompt = (chain["footer"] + "\n\n" + task["prompt"]) if chain["step"] > 0 else task["prompt"]
        resume = chain["step"] > 0
    cmd = build_command(config, task, cond, prompt, session_id, resume)
    tag = f"{task['label']} / {cond['label']} / {mode['label']}" + (f" step {chain['step'] + 1}" if chain else "") + f" / rep {rep_index}"
    print(f"\n=== {tag} -> {run_id}", flush=True)
    if dry_run:
        print("   would run:", " ".join(c if len(c) < 50 else c[:47] + "..." for c in cmd))
        return {"status": "dry_run"}
    out_dir.mkdir(parents=True)
    if chain is None:
        base_commit = repo.reset_to(branch, wipe_scratch=True)
    else:
        base_commit = chain["prev_checkpoint"]
    proj_dir = clear_auto_memory(config) if chain is None or chain["step"] == 0 else (pathlib.Path.home() / ".claude" / "projects" / escaped_project_dir(config["repo_dir"]))
    (out_dir / "command.json").write_text(json.dumps({"cmd": cmd, "cwd": config["repo_dir"]}, indent=2), encoding="utf-8")
    proc = run_claude(cmd, config["repo_dir"], config["timeouts_s"][task["length"]], out_dir)
    events = metrics.read_jsonl(out_dir / "stream.jsonl")
    ss = metrics.stream_summary(events)
    result = ss["result"]
    (out_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out_dir / "init.json").write_text(json.dumps(ss["init"], indent=2), encoding="utf-8")
    found = copy_transcripts(proj_dir, session_id, out_dir)
    # Checkpoint the agent's state, then diff against the start of this task.
    checkpoint = repo.checkpoint(f"harness checkpoint after {task['label']}")
    diff_text, diff_stat = repo.diff(base_commit, checkpoint)
    (out_dir / "diff.patch").write_text(diff_text, encoding="utf-8")
    (out_dir / "diff.stat").write_text(diff_stat, encoding="utf-8")
    tmp = pathlib.Path(config["repo_dir"]) / ".claude" / "tmp"
    if tmp.exists():
        shutil.copytree(tmp, out_dir / "claude_tmp", dirs_exist_ok=True)
    stderr_text = (out_dir / "stderr.txt").read_text(encoding="utf-8", errors="replace")
    rate_limited = detect_rate_limit(result, stderr_text, ss)
    if rate_limited:
        print("   rate limit detected; this attempt is set aside", flush=True)
        status, checks = "aborted_rate_limit", None
    else:
        checks = run_checks(config, task, repo, out_dir, diff_text)
        status = "completed" if result is not None else "no_result"
    # Hidden files and build output must not leak into the next chain step.
    repo.restore(checkpoint)
    if status == "completed":
        shutil.copyfile(out_dir / "diff.patch", HERE / config["blind_dir"] / f"{blind_id}.diff")
        (HERE / config["blind_dir"] / f"{blind_id}.prompt.md").write_text(task["prompt_body"] if "prompt_body" in task else task["prompt"], encoding="utf-8")
        if task["type"] == "find":
            (HERE / config["blind_dir"] / f"{blind_id}.answer.md").write_text(str(result.get("result", "")), encoding="utf-8")
        append_mapping(config, blind_id, {"run_id": run_id, "task_id": task["id"], "condition_id": cond["id"], "session_mode": mode["label"]})
        append_grading_row(config, blind_id, task)
    tsum = metrics.transcript_summary(out_dir / "transcript" / "main.jsonl")
    subs = metrics.subagent_summary(out_dir / "transcript" / "subagents")
    cumulative_usage = (result or {}).get("modelUsage")
    delta_usage, is_cumulative = usage_delta(cumulative_usage, chain["prev_usage"] if chain else None)
    cost = metrics.compute_cost(delta_usage, ss["calls"], prices)
    main_model = (ss["init"] or {}).get("model")
    ctx_window = None
    for m, mu in (cumulative_usage or {}).items():
        if metrics.norm_model(m) == metrics.norm_model(main_model or m):
            ctx_window = mu.get("contextWindow")
            break
    run = {
        "run_id": run_id, "blind_id": blind_id if status == "completed" else None, "session_id": session_id,
        "task_id": task["id"], "task_label": task["label"], "task_type": task["type"], "task_length": task["length"],
        "condition_id": cond["id"], "condition_label": cond["label"], "rep_index": rep_index,
        "session_mode": mode["label"], "session_mode_id": mode["id"],
        "chain_id": chain["chain_id"] if chain else None, "chain_step": chain["step"] if chain else None,
        "branch": branch, "base_commit": base_commit, "checkpoint_commit": checkpoint, "status": status,
        "process": proc, "exit_code": proc["rc"],
        "result_subtype": (result or {}).get("subtype"), "is_error": (result or {}).get("is_error"),
        "num_turns": (result or {}).get("num_turns"), "duration_ms": (result or {}).get("duration_ms"),
        "duration_api_ms": (result or {}).get("duration_api_ms"), "claude_total_cost_usd": (result or {}).get("total_cost_usd"),
        "claude_cost_cumulative": chain is not None, "usage_is_cumulative": is_cumulative,
        "cost": cost, "model_usage": delta_usage, "model_usage_cumulative": cumulative_usage,
        "stream": {k: ss[k] for k in ("per_model", "main_api_calls", "sub_api_calls", "sub_calls_by_type", "context_end_tokens",
                                       "context_max_tokens", "shunt_denials", "tool_errors", "permission_denied_events", "api_retries", "api_retry_errors")},
        "context_window": ctx_window,
        "context_end_ratio": (ss["context_end_tokens"] / ctx_window) if (ss["context_end_tokens"] and ctx_window) else None,
        "transcript": tsum, "transcripts_found": found, "subagents": subs, "rework": metrics.rework_stats(subs),
        "subagent_stats": (result or {}).get("subagent_stats"),
        "init_plugins": [p.get("name") for p in ((ss["init"] or {}).get("plugins") or [])],
        "init_agents": (ss["init"] or {}).get("agents"), "init_model": main_model,
        "init_permission_mode": (ss["init"] or {}).get("permissionMode"),
        "diff": {"diff_bytes": len(diff_text.encode()), "files_changed": [l.split("\t", 1)[-1] for l in diff_stat.strip().splitlines() if "\t" in l]},
        "checks": checks, "final_text_chars": len(str((result or {}).get("result", ""))),
    }
    (out_dir / "run.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
    c = checks or {}
    print(f"   status={status} subtype={run['result_subtype']} turns={run['num_turns']} wall={proc['wall_s']}s "
          f"cost=${cost['total_usd']:.3f} ctx_end={ss['context_end_tokens']} checks={'all_pass=' + str(c.get('all_pass')) if c else 'n/a'} "
          f"subagents={found['subagents']} shunt={ss['shunt_denials']}", flush=True)
    run["_checkpoint"] = checkpoint
    run["_cumulative_usage"] = cumulative_usage
    return run


def run_chain(config, prices, repo, tasks, cond, mode, rep_index, results_dir, dry_run):
    chain_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    footer = (HERE / config["chain_footer_file"]).read_text(encoding="utf-8").strip()
    branch = load_json(HERE / config["tasks_file"])["chain_branches"][cond["id"]]["branch"]
    print(f"\n##### chain {chain_id[:8]} / {cond['label']} / rep {rep_index}: {' > '.join(t['label'] for t in tasks)}", flush=True)
    if dry_run:
        for i, t in enumerate(tasks):
            one_run(config, prices, repo, t, cond, mode, rep_index, results_dir, True,
                    chain={"session_id": session_id, "chain_id": chain_id, "step": i, "prev_checkpoint": None, "prev_usage": None, "footer": footer})
        return
    prev_checkpoint = repo.reset_to(branch, wipe_scratch=True)
    prev_usage = None
    for i, t in enumerate(tasks):
        attempts = 0
        while True:
            run = one_run(config, prices, repo, t, cond, mode, rep_index, results_dir, False,
                          chain={"session_id": session_id, "chain_id": chain_id, "step": i, "prev_checkpoint": prev_checkpoint, "prev_usage": prev_usage, "footer": footer})
            if run.get("status") != "aborted_rate_limit":
                break
            attempts += 1
            if attempts > config["rate_limit_max_retries"]:
                raise SystemExit("too many rate-limit aborts; stopping")
            print(f"   waiting {config['rate_limit_wait_s']}s before retrying this chain step", flush=True)
            time.sleep(config["rate_limit_wait_s"])
        prev_checkpoint = run["_checkpoint"]
        prev_usage = run["_cumulative_usage"] or prev_usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config2.json")
    ap.add_argument("--tasks", default="all")
    ap.add_argument("--conditions", default="A,B")
    ap.add_argument("--modes", default="fresh,chain")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    config = load_json(HERE / args.config)
    prices = load_json(HERE / config["prices_file"])
    tasks_doc = load_json(HERE / config["tasks_file"])
    tasks = tasks_doc["tasks"]
    if args.tasks != "all":
        wanted = [x.strip() for x in args.tasks.split(",")]
        by_label = {t["label"]: t for t in tasks}
        missing = [w for w in wanted if w not in by_label]
        if missing:
            raise SystemExit(f"unknown task labels: {missing}")
        tasks = [by_label[w] for w in wanted]
    conds = [c for c in config["conditions"] if c["label"] in [x.strip() for x in args.conditions.split(",")]]
    modes = [m for m in config["session_modes"] if m["label"] in [x.strip() for x in args.modes.split(",")]]
    results_dir = HERE / config["results_dir"]
    results_dir.mkdir(parents=True, exist_ok=True)
    (HERE / config["blind_dir"]).mkdir(parents=True, exist_ok=True)
    repo = Repo(config)
    rng = random.Random(args.seed if args.seed is not None else int(time.time()))
    chain_tasks = [t for label in tasks_doc.get("chain_order", []) for t in tasks if t["label"] == label]
    last_chain_task = chain_tasks[-1] if chain_tasks else None
    for rep in range(args.reps):
        for mode in modes:
            if mode["label"] == "fresh":
                for task in tasks:
                    order = list(conds)
                    rng.shuffle(order)
                    for cond in order:
                        if existing_completed(results_dir, task["id"], cond["id"], "fresh") >= args.reps:
                            continue
                        attempts = 0
                        while True:
                            run = one_run(config, prices, repo, task, cond, mode, rep, results_dir, args.dry_run)
                            if run.get("status") != "aborted_rate_limit":
                                break
                            attempts += 1
                            if attempts > config["rate_limit_max_retries"]:
                                raise SystemExit("too many rate-limit aborts; stopping")
                            print(f"   waiting {config['rate_limit_wait_s']}s before retrying", flush=True)
                            time.sleep(config["rate_limit_wait_s"])
            elif mode["label"] == "chain" and chain_tasks:
                order = list(conds)
                rng.shuffle(order)
                for cond in order:
                    if existing_completed(results_dir, last_chain_task["id"], cond["id"], "chain") >= args.reps:
                        continue
                    run_chain(config, prices, repo, chain_tasks, cond, mode, rep, results_dir, args.dry_run)
    if not args.dry_run:
        repo.reset_to("base", wipe_scratch=True)
    print("\ndone")


if __name__ == "__main__":
    main()
