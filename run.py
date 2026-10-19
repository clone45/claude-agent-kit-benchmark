#!/usr/bin/env python3
"""Run tasks headlessly in both conditions, reset the repo between runs, save everything.

usage: run.py --tasks B1,Q1 --conditions A,B --reps 1 [--dry-run] [--order interleave|sequential]

`--reps N` is a target: existing completed runs for a (task, condition) cell count toward it, so
re-running the same command after a pause only fills the gaps. Each run writes
results/runs/<run-uuid>/ with stream.jsonl, result.json, init.json, stderr.txt, diff.patch,
transcript/ (main + subagents), checks/, run.json, and a blind copy of the diff under blind/.
"""

from __future__ import annotations

import argparse
import ast
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


def sh(cmd, cwd=None, timeout=None, env=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout, env=env)
        return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as e:
        return {"rc": None, "stdout": (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""),
                "stderr": (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or ""), "timed_out": True}


def reset_repo(config, branch):
    repo = config["repo_dir"]
    keep = []
    for k in config["clean_keep"]:
        keep += ["-e", k]
    for cmd in (["git", "checkout", "-q", "-f", branch], ["git", "reset", "-q", "--hard"], ["git", "clean", "-qfdx", *keep]):
        r = sh(cmd, cwd=repo)
        if r["rc"] != 0:
            raise SystemExit(f"reset failed: {cmd}: {r['stderr']}")
    status = sh(["git", "status", "--porcelain"], cwd=repo)["stdout"].strip()
    if status:
        raise SystemExit(f"repo not clean after reset:\n{status}")
    return sh(["git", "rev-parse", "HEAD"], cwd=repo)["stdout"].strip()


def clear_auto_memory(config):
    proj = pathlib.Path.home() / ".claude" / "projects" / escaped_project_dir(config["repo_dir"])
    mem = proj / "memory"
    if mem.exists():
        shutil.rmtree(mem)
    return proj


def build_command(config, task, cond, prompt, session_id):
    budget = config["max_budget_usd"][task["length"]]
    cmd = [config["claude_bin"], "-p", prompt,
           "--model", config["model"], "--effort", config["effort"],
           "--permission-mode", config["permission_mode"],
           "--setting-sources", "project,local", "--strict-mcp-config",
           "--output-format", "stream-json", "--verbose", "--forward-subagent-text", "--include-hook-events",
           "--max-budget-usd", str(budget), "--session-id", session_id]
    if cond["plugin"]:
        cmd += ["--plugin-dir", config["plugin_dir"]]
    return cmd


def run_claude(cmd, cwd, timeout, out_dir):
    env = dict(os.environ)
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SSE_PORT"):
        env.pop(k, None)  # the runner may itself be launched from inside a Claude Code session
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
    main = proj_dir / f"{session_id}.jsonl"
    found = {"main": False, "subagents": 0}
    time.sleep(2)  # transcript writes are asynchronous
    if main.exists():
        shutil.copyfile(main, tdir / "main.jsonl")
        found["main"] = True
    sub = proj_dir / session_id / "subagents"
    if sub.exists():
        shutil.copytree(sub, tdir / "subagents", dirs_exist_ok=True)
        found["subagents"] = len(list(sub.glob("agent-*.jsonl")))
    return found


def snapshot_diff(config, base_commit, out_dir):
    repo = config["repo_dir"]
    sh(["git", "add", "-A"], cwd=repo)
    diff = sh(["git", "diff", "--cached", base_commit], cwd=repo)["stdout"]
    stat = sh(["git", "diff", "--cached", "--stat", base_commit], cwd=repo)["stdout"]
    names = sh(["git", "diff", "--cached", "--name-status", base_commit], cwd=repo)["stdout"]
    sh(["git", "reset", "-q"], cwd=repo)
    (out_dir / "diff.patch").write_text(diff, encoding="utf-8")
    (out_dir / "diff.stat").write_text(stat + "\n" + names, encoding="utf-8")
    tmp = pathlib.Path(repo) / ".claude" / "tmp"
    if tmp.exists():
        shutil.copytree(tmp, out_dir / "claude_tmp", dirs_exist_ok=True)
    return {"diff_bytes": len(diff.encode()), "files_changed": [line.split("\t", 1)[-1] for line in names.strip().splitlines()]}


def function_lengths(repo, targets):
    out = {}
    for rel, fname in targets:
        p = pathlib.Path(repo) / rel
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            out[f"{rel}:{fname}"] = f"parse error: {e}"
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fname:
                out[f"{rel}:{fname}"] = node.end_lineno - node.lineno + 1
    return out


def run_checks(config, task, out_dir):
    repo = pathlib.Path(config["repo_dir"])
    py = str(repo / config["venv_python"])
    cdir = out_dir / "checks"
    cdir.mkdir(exist_ok=True)
    timeout = config["timeouts_s"]["check"]
    results = {}

    def record(name, r):
        (cdir / f"{name}.txt").write_text(f"rc={r['rc']} timed_out={r['timed_out']}\n--- stdout\n{r['stdout']}\n--- stderr\n{r['stderr']}", encoding="utf-8")
        tail = (r["stdout"].strip().splitlines() or [""])[-1]
        results[name] = {"pass": r["rc"] == 0, "rc": r["rc"], "timed_out": r["timed_out"], "tail": tail[:300]}

    if "no_changes" in task["checks"]:
        diff = (out_dir / "diff.patch").read_text(encoding="utf-8")
        results["no_changes"] = {"pass": diff.strip() == "", "diff_bytes": len(diff)}
    if task["function_metrics"]:
        results["function_lengths"] = function_lengths(repo, task["function_metrics"])
    if "hidden" in task["checks"] and task["hidden_tests"]:
        hidden_root = HERE / "tasks" / "hidden" / task["id"]
        for rel in task["hidden_tests"]:
            dest = repo / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(hidden_root / rel, dest)
        pytest_targets = [f for f in task["hidden_tests"] if f.startswith("tests/") and not f.startswith("tests/typing/")]
        if pytest_targets:
            record("hidden", sh([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", *pytest_targets], cwd=repo, timeout=timeout))
    if "full" in task["checks"]:
        record("full", sh([py, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=repo, timeout=timeout))
    if "ruff" in task["checks"]:
        record("ruff", sh([str(repo / ".venv" / "bin" / "ruff"), "check", "src", "tests"], cwd=repo, timeout=timeout))
    if "format" in task["checks"]:
        record("format", sh([str(repo / ".venv" / "bin" / "ruff"), "format", "--check", "src", "tests"], cwd=repo, timeout=timeout))
    if "mypy" in task["checks"]:
        record("mypy", sh([str(repo / ".venv" / "bin" / "mypy")], cwd=repo, timeout=timeout))
    gate = [k for k in ("hidden", "full", "ruff", "format", "mypy", "no_changes") if k in results]
    results["all_pass"] = all(results[k]["pass"] for k in gate) if gate else None
    return results


def detect_rate_limit(result, stderr_text, stream_summary):
    texts = []
    if result:
        texts.append(str(result.get("result", "")))
        texts.extend(str(x) for x in (result.get("errors") or []))
        if result.get("api_error_status") == 429:
            return True
    texts.append(stderr_text[-4000:])
    if any(e in ("rate_limit",) for e in stream_summary.get("api_retry_errors", [])) and (result is None or result.get("is_error")):
        return True
    return any(RATE_LIMIT_RE.search(t) for t in texts if t) and (result is None or result.get("is_error"))


def existing_completed(results_dir, task_id, cond_id):
    n = 0
    for rj in results_dir.glob("*/run.json"):
        try:
            d = load_json(rj)
        except json.JSONDecodeError:
            continue
        if d.get("task_id") == task_id and d.get("condition_id") == cond_id and d.get("status") == "completed":
            n += 1
    return n


def append_mapping(blind_id, info):
    p = HERE / "private" / "mapping.json"
    m = load_json(p) if p.exists() else {}
    m[blind_id] = info
    p.write_text(json.dumps(m, indent=2), encoding="utf-8")


def append_grading_row(blind_id, task):
    p = HERE / "blind" / "grading_sheet.csv"
    new = not p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["blind_id", "task", "type", "score_1_to_5", "notes"])
        w.writerow([blind_id, task["label"], task["type"], "", ""])


def one_run(config, prices, task, cond, rep_index, results_dir, dry_run):
    run_id = str(uuid.uuid4())
    blind_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    out_dir = results_dir / run_id
    branch = task["branches"][cond["id"]]["branch"]
    cmd = build_command(config, task, cond, task["prompt"], session_id)
    print(f"\n=== {task['label']} / {cond['label']} / rep {rep_index} -> {run_id}", flush=True)
    if dry_run:
        print("   would run:", " ".join(c if len(c) < 60 else c[:57] + "..." for c in cmd))
        return {"status": "dry_run"}
    out_dir.mkdir(parents=True)
    base_commit = reset_repo(config, branch)
    proj_dir = clear_auto_memory(config)
    (out_dir / "command.json").write_text(json.dumps({"cmd": cmd, "cwd": config["repo_dir"]}, indent=2), encoding="utf-8")
    timeout = config["timeouts_s"][task["length"]]
    proc = run_claude(cmd, config["repo_dir"], timeout, out_dir)
    events = metrics.read_jsonl(out_dir / "stream.jsonl")
    ss = metrics.stream_summary(events)
    result = ss["result"]
    (out_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out_dir / "init.json").write_text(json.dumps(ss["init"], indent=2), encoding="utf-8")
    found = copy_transcripts(proj_dir, session_id, out_dir)
    diff_info = snapshot_diff(config, base_commit, out_dir)
    stderr_text = (out_dir / "stderr.txt").read_text(encoding="utf-8", errors="replace")
    rate_limited = detect_rate_limit(result, stderr_text, ss)
    if rate_limited:
        print("   rate limit detected; this attempt is set aside", flush=True)
        status = "aborted_rate_limit"
        checks = None
    else:
        checks = run_checks(config, task, out_dir)
        status = "completed" if result is not None else "no_result"
    # Blind artifacts only for completed runs
    if status == "completed":
        shutil.copyfile(out_dir / "diff.patch", HERE / "blind" / f"{blind_id}.diff")
        (HERE / "blind" / f"{blind_id}.prompt.md").write_text(task["prompt"], encoding="utf-8")
        if task["type"] == "find":
            (HERE / "blind" / f"{blind_id}.answer.md").write_text(str(result.get("result", "")), encoding="utf-8")
        append_mapping(blind_id, {"run_id": run_id, "task_id": task["id"], "condition_id": cond["id"]})
        append_grading_row(blind_id, task)
    tsum = metrics.transcript_summary(out_dir / "transcript" / "main.jsonl")
    subs = metrics.subagent_summary(out_dir / "transcript" / "subagents")
    cost = metrics.compute_cost((result or {}).get("modelUsage"), ss["calls"], prices)
    main_model = (ss["init"] or {}).get("model")
    ctx_window = None
    for m, mu in ((result or {}).get("modelUsage") or {}).items():
        if metrics.norm_model(m) == metrics.norm_model(main_model or m):
            ctx_window = mu.get("contextWindow")
            break
    run = {
        "run_id": run_id, "blind_id": blind_id if status == "completed" else None, "session_id": session_id,
        "task_id": task["id"], "task_label": task["label"], "task_type": task["type"], "task_length": task["length"],
        "condition_id": cond["id"], "condition_label": cond["label"], "rep_index": rep_index,
        "branch": branch, "base_commit": base_commit, "status": status,
        "process": proc, "exit_code": proc["rc"],
        "result_subtype": (result or {}).get("subtype"), "is_error": (result or {}).get("is_error"),
        "num_turns": (result or {}).get("num_turns"), "duration_ms": (result or {}).get("duration_ms"),
        "duration_api_ms": (result or {}).get("duration_api_ms"), "claude_total_cost_usd": (result or {}).get("total_cost_usd"),
        "cost": cost, "model_usage": (result or {}).get("modelUsage"),
        "stream": {k: ss[k] for k in ("per_model", "main_api_calls", "sub_api_calls", "sub_calls_by_type", "context_end_tokens",
                                       "context_max_tokens", "shunt_denials", "tool_errors", "permission_denied_events", "api_retries", "api_retry_errors")},
        "context_window": ctx_window,
        "context_end_ratio": (ss["context_end_tokens"] / ctx_window) if (ss["context_end_tokens"] and ctx_window) else None,
        "transcript": tsum, "transcripts_found": found, "subagents": subs, "rework": metrics.rework_stats(subs),
        "subagent_stats": (result or {}).get("subagent_stats"),
        "init_plugins": [p.get("name") for p in ((ss["init"] or {}).get("plugins") or [])],
        "init_agents": (ss["init"] or {}).get("agents"), "init_model": main_model,
        "init_permission_mode": (ss["init"] or {}).get("permissionMode"),
        "diff": diff_info, "checks": checks, "final_text_chars": len(str((result or {}).get("result", ""))),
    }
    (out_dir / "run.json").write_text(json.dumps(run, indent=2), encoding="utf-8")
    c = checks or {}
    print(f"   status={status} subtype={run['result_subtype']} turns={run['num_turns']} wall={proc['wall_s']}s "
          f"cost=${cost['total_usd']:.3f} (claude ${run['claude_total_cost_usd']}) ctx_end={ss['context_end_tokens']} "
          f"checks={'all_pass=' + str(c.get('all_pass')) if c else 'n/a'} subagents={found['subagents']}", flush=True)
    return run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="all", help="comma-separated task labels, or all")
    ap.add_argument("--conditions", default="A,B")
    ap.add_argument("--reps", type=int, default=1, help="target completed runs per task and condition")
    ap.add_argument("--order", choices=["interleave", "sequential"], default="interleave")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    config = load_json(HERE / "config.json")
    prices = load_json(HERE / config["prices_file"])
    tasks_doc = load_json(HERE / "tasks.json")
    tasks = tasks_doc["tasks"]
    if args.tasks != "all":
        wanted = [x.strip() for x in args.tasks.split(",")]
        by_label = {t["label"]: t for t in tasks}
        missing = [w for w in wanted if w not in by_label]
        if missing:
            raise SystemExit(f"unknown task labels: {missing}")
        tasks = [by_label[w] for w in wanted]
    conds = [c for c in config["conditions"] if c["label"] in [x.strip() for x in args.conditions.split(",")]]
    results_dir = HERE / "results" / "runs"
    results_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed if args.seed is not None else int(time.time()))
    plan = []
    for rep in range(args.reps):
        for task in tasks:
            order = list(conds)
            if args.order == "interleave":
                rng.shuffle(order)
            for cond in order:
                plan.append((rep, task, cond))
    print(f"plan: {len(plan)} cells over {len(tasks)} tasks x {len(conds)} conditions x {args.reps} reps (gaps only)")
    for rep, task, cond in plan:
        have = existing_completed(results_dir, task["id"], cond["id"])
        if have >= args.reps:
            continue
        attempts = 0
        while True:
            run = one_run(config, prices, task, cond, have, results_dir, args.dry_run)
            if run.get("status") != "aborted_rate_limit":
                break
            attempts += 1
            if attempts > config["rate_limit_max_retries"]:
                raise SystemExit("too many rate-limit aborts; stopping")
            wait = config["rate_limit_wait_s"]
            print(f"   waiting {wait}s before retrying", flush=True)
            time.sleep(wait)
    print("\ndone")


if __name__ == "__main__":
    main()
