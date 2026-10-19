#!/usr/bin/env python3
"""Summarize completed runs: per task type and overall, per condition, with spread.

usage: summarize.py [--config config.json] [--out <dir>/summary.md] [--csv <dir>/runs.csv]
Reads <results_dir>/*/run.json, the config's tasks file, and the grading sheet if filled in.
When runs carry more than one session mode (fresh, chain), every table is split by mode.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib
import statistics
import sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
import metrics  # noqa: E402

TYPES = ("bugfix", "feature", "refactor", "find", "long")


def load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def stats(values):
    vals = [v for v in values if isinstance(v, (int, float))]
    if not vals:
        return None
    return {"n": len(vals), "mean": statistics.mean(vals), "median": statistics.median(vals),
            "min": min(vals), "max": max(vals), "stdev": statistics.stdev(vals) if len(vals) > 1 else 0.0}


def fmt(s, money=False, pct=False, digits=2):
    if not s:
        return "n/a"
    if money:
        return f"${s['mean']:.2f} (${s['min']:.2f} to ${s['max']:.2f})"
    if pct:
        return f"{100 * s['mean']:.0f}%"
    return f"{s['mean']:.{digits}f} ({s['min']:.{digits}f} to {s['max']:.{digits}f})"


def model_class(model):
    m = model.lower()
    for k in ("opus", "sonnet", "haiku", "fable"):
        if k in m:
            return k
    return "other"


def row_from_run(r, grades, prices, results_dir):
    run_dir = results_dir / r["run_id"]
    cold = metrics.cold_start(metrics.stream_summary(metrics.read_jsonl(run_dir / "stream.jsonl"))["calls"], prices)
    cost_by_class = defaultdict(float)
    tokens = defaultdict(lambda: defaultdict(int))
    for model, c in (r.get("cost", {}).get("by_model") or {}).items():
        mc = model_class(model)
        cost_by_class[mc] += c["cost_usd"]
        for k in ("input_tokens", "cache_read_tokens", "cache_create_tokens", "output_tokens"):
            tokens[mc][k] += c[k] or 0
    checks = r.get("checks") or {}
    check_names = [k for k, v in checks.items() if isinstance(v, dict) and "pass" in v]
    hidden = (checks.get("hidden") or {}).get("pass") if "hidden" in checks else None
    full_keys = [k for k in ("full", "tests") if k in checks]
    full = all(checks[k]["pass"] for k in full_keys) if full_keys else None
    lint_keys = [k for k in check_names if k in ("ruff", "format", "mypy") or k.startswith("compile")]
    lint = all(checks[k]["pass"] for k in lint_keys) if lint_keys else None
    return {
        "run_id": r["run_id"], "blind_id": r.get("blind_id"), "task": r["task_label"], "type": r["task_type"],
        "condition": r["condition_label"], "mode": r.get("session_mode") or "fresh", "chain_step": r.get("chain_step"),
        "status": r["status"], "subtype": r.get("result_subtype"),
        "cost_usd": r.get("cost", {}).get("total_usd"), "claude_cost_usd": r.get("claude_total_cost_usd"),
        "cost_warm_usd": (r.get("cost", {}).get("total_usd") or 0) - cold["cold_write_usd"],
        "first_call_cache_create": cold["first_call_cache_create_tokens"], "first_call_cache_read": cold["first_call_cache_read_tokens"],
        "cost_opus": cost_by_class.get("opus", 0.0), "cost_sonnet": cost_by_class.get("sonnet", 0.0), "cost_haiku": cost_by_class.get("haiku", 0.0),
        "wall_s": r.get("process", {}).get("wall_s"), "api_s": (r.get("duration_api_ms") or 0) / 1000 if r.get("duration_api_ms") else None,
        "turns": r.get("num_turns"), "main_api_calls": r.get("stream", {}).get("main_api_calls"), "sub_api_calls": r.get("stream", {}).get("sub_api_calls"),
        "subagents": r.get("transcripts_found", {}).get("subagents"),
        "context_end_tokens": r.get("stream", {}).get("context_end_tokens"), "context_max_tokens": r.get("stream", {}).get("context_max_tokens"),
        "context_end_ratio": r.get("context_end_ratio"), "compactions": r.get("transcript", {}).get("compactions"),
        "shunt_denials": r.get("stream", {}).get("shunt_denials"),
        "refuter_fail": r.get("rework", {}).get("refuter_fail"), "refuter_runs": r.get("rework", {}).get("refuter_runs"), "builder_runs": r.get("rework", {}).get("builder_runs"),
        "hidden_pass": hidden, "full_pass": full, "lint_pass": lint,
        "no_changes": (checks.get("no_changes") or {}).get("pass") if "no_changes" in checks else None,
        "all_pass": checks.get("all_pass"), "function_lengths": checks.get("function_lengths"),
        "tokens": {k: dict(v) for k, v in tokens.items()}, "grade": grades.get(r.get("blind_id")),
    }


def pass_rate(rows, key):
    vals = [1.0 if x[key] else 0.0 for x in rows if x[key] is not None]
    return stats(vals) if vals else None


def section(rows, title):
    out = [f"### {title}", ""]
    conds = sorted({x["condition"] for x in rows})
    header = ["Measure"] + [f"Condition {c} (n={sum(1 for x in rows if x['condition'] == c)})" for c in conds]
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "---|" * len(header))

    def line(label, fn):
        out.append("| " + " | ".join([label] + [fn([x for x in rows if x["condition"] == c]) for c in conds]) + " |")

    line("Cost per run, mean (min to max)", lambda rs: fmt(stats([x["cost_usd"] for x in rs]), money=True))
    line("Cost stdev", lambda rs: (lambda s: f"${s['stdev']:.2f}" if s else "n/a")(stats([x["cost_usd"] for x in rs])))
    line("Cost excluding first-call cache write", lambda rs: fmt(stats([x["cost_warm_usd"] for x in rs]), money=True))
    line("First-call cache write, tokens (cold start)", lambda rs: fmt(stats([x["first_call_cache_create"] for x in rs]), digits=0))
    line("Opus share of cost", lambda rs: (lambda a, b: f"{100 * a / b:.0f}%" if b else "n/a")(sum(x["cost_opus"] for x in rs), sum(x["cost_usd"] or 0 for x in rs)))
    line("Sonnet + Haiku cost per run", lambda rs: fmt(stats([x["cost_sonnet"] + x["cost_haiku"] for x in rs]), money=True))
    line("Wall time, seconds", lambda rs: fmt(stats([x["wall_s"] for x in rs]), digits=0))
    line("Main-session API calls", lambda rs: fmt(stats([x["main_api_calls"] for x in rs]), digits=0))
    line("Subagent API calls", lambda rs: fmt(stats([x["sub_api_calls"] for x in rs]), digits=0))
    line("Context at end, tokens", lambda rs: fmt(stats([x["context_end_tokens"] for x in rs]), digits=0))
    line("Context at end, share of window", lambda rs: (lambda s: f"{100 * s['mean']:.1f}% (max {100 * s['max']:.1f}%)" if s else "n/a")(stats([x["context_end_ratio"] for x in rs])))
    line("Compactions", lambda rs: fmt(stats([x["compactions"] for x in rs]), digits=1))
    line("Read-budget denials (hook)", lambda rs: fmt(stats([x["shunt_denials"] for x in rs]), digits=1))
    line("Refuter FAIL verdicts (rework)", lambda rs: fmt(stats([x["refuter_fail"] for x in rs]), digits=1))
    line("Hidden tests pass", lambda rs: fmt(pass_rate(rs, "hidden_pass"), pct=True))
    line("Full suite / standalone tests pass", lambda rs: fmt(pass_rate(rs, "full_pass"), pct=True))
    line("Lint, types, compile pass", lambda rs: fmt(pass_rate(rs, "lint_pass"), pct=True))
    line("No file changes (find tasks)", lambda rs: fmt(pass_rate(rs, "no_changes"), pct=True))
    line("All automatic checks pass", lambda rs: fmt(pass_rate(rs, "all_pass"), pct=True))
    line("Blind grade, mean 1 to 5", lambda rs: fmt(stats([x["grade"] for x in rs]), digits=2))
    if len(conds) == 2:
        a = [x for x in rows if x["condition"] == conds[0]]
        b = [x for x in rows if x["condition"] == conds[1]]
        for key, label in (("cost_usd", "cost"), ("wall_s", "wall time")):
            sa, sb = stats([x[key] for x in a]), stats([x[key] for x in b])
            if sa and sb and sa["n"] > 1 and sb["n"] > 1:
                pooled = ((sa["stdev"] ** 2 + sb["stdev"] ** 2) / 2) ** 0.5
                diff = sb["mean"] - sa["mean"]
                verdict = "smaller than the run-to-run spread" if pooled and abs(diff) < pooled else "larger than the run-to-run spread"
                out.append(f"| {conds[1]} minus {conds[0]}, {label} | {diff:+.2f} | pooled stdev {pooled:.2f}: difference is {verdict} |")
    out.append("")
    return out


def per_task_table(rows):
    out = ["### Per task", "", "| Task | Type | Mode | Cond | n | Cost mean | Cost min to max | Wall s | Context end | Checks pass | Hidden pass | Grade |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    keys = sorted({(x["task"], x["type"], x["mode"]) for x in rows})
    for task, typ, mode in keys:
        for c in sorted({x["condition"] for x in rows}):
            rs = [x for x in rows if x["task"] == task and x["condition"] == c and x["mode"] == mode]
            if not rs:
                continue
            cs = stats([x["cost_usd"] for x in rs])
            ws = stats([x["wall_s"] for x in rs])
            xs = stats([x["context_end_tokens"] for x in rs])
            out.append(f"| {task} | {typ} | {mode} | {c} | {len(rs)} | ${cs['mean']:.2f} | ${cs['min']:.2f} to ${cs['max']:.2f} | {ws['mean']:.0f} | "
                       f"{xs['mean']:.0f} | {fmt(pass_rate(rs, 'all_pass'), pct=True)} | {fmt(pass_rate(rs, 'hidden_pass'), pct=True)} | {fmt(stats([x['grade'] for x in rs]))} |")
    out.append("")
    return out


def chain_step_table(rows):
    chain = [x for x in rows if x["mode"] == "chain" and x["chain_step"] is not None]
    if not chain:
        return []
    out = ["### Chained session, by step", "", "| Step | Task | Cond | n | Cost mean | Context at end | Checks pass |", "|---|---|---|---|---|---|---|"]
    for step in sorted({x["chain_step"] for x in chain}):
        for c in sorted({x["condition"] for x in chain}):
            rs = [x for x in chain if x["chain_step"] == step and x["condition"] == c]
            if not rs:
                continue
            cs = stats([x["cost_usd"] for x in rs])
            xs = stats([x["context_end_tokens"] for x in rs])
            out.append(f"| {step + 1} | {rs[0]['task']} | {c} | {len(rs)} | ${cs['mean']:.2f} | {xs['mean']:.0f} | {fmt(pass_rate(rs, 'all_pass'), pct=True)} |")
    out.append("")
    return out


def load_grades(path):
    grades = {}
    p = pathlib.Path(path)
    if p.exists():
        with p.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                v = (row.get("score_1_to_5") or "").strip()
                if v:
                    try:
                        grades[row["blind_id"]] = float(v)
                    except ValueError:
                        pass
    return grades


def collect_rows(config):
    prices = load_json(HERE / config["prices_file"])
    results_dir = HERE / config.get("results_dir", "results/runs")
    grades = load_grades(HERE / config.get("grading_sheet", "blind/grading_sheet.csv"))
    rows, unpriced = [], set()
    for rj in sorted(results_dir.glob("*/run.json")):
        r = load_json(rj)
        if r.get("status") != "completed":
            continue
        rows.append(row_from_run(r, grades, prices, results_dir))
        unpriced.update((r.get("cost") or {}).get("unpriced_models", []))
    return rows, sorted(unpriced)


def render(rows, unpriced):
    lines = [f"# Summary of {len(rows)} completed runs", ""]
    if unpriced:
        lines += [f"Warning: models with no price entry (cost undercounted): {', '.join(unpriced)}", ""]
    not_success = [x for x in rows if x["subtype"] != "success"]
    if not_success:
        lines += [f"Runs that did not end with a success result: {len(not_success)} ({', '.join(sorted({str(x['subtype']) for x in not_success}))}). They are included in the tables.", ""]
    modes = sorted({x["mode"] for x in rows})
    for mode in modes:
        rs_mode = [x for x in rows if x["mode"] == mode]
        label = "" if len(modes) == 1 else f", {mode} sessions"
        lines += section(rs_mode, f"Overall{label}")
        for typ in TYPES:
            rs = [x for x in rs_mode if x["type"] == typ]
            if rs:
                lines += section(rs, f"Task type: {typ}{label}")
    lines += chain_step_table(rows)
    lines += per_task_table(rows)
    graded = sum(1 for x in rows if x["grade"] is not None)
    lines.append(f"Blind grades recorded: {graded} of {len(rows)} runs.")
    return "\n".join(lines)


def write_csv(rows, path):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        fields = [k for k in rows[0].keys() if k not in ("tokens", "function_lengths")] + ["opus_in", "opus_cache_read", "opus_cache_create", "opus_out", "sonnet_out", "haiku_out", "function_lengths"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for x in rows:
            t = x["tokens"]
            row = {k: v for k, v in x.items() if k not in ("tokens", "function_lengths")}
            row.update({"opus_in": t.get("opus", {}).get("input_tokens"), "opus_cache_read": t.get("opus", {}).get("cache_read_tokens"),
                        "opus_cache_create": t.get("opus", {}).get("cache_create_tokens"), "opus_out": t.get("opus", {}).get("output_tokens"),
                        "sonnet_out": t.get("sonnet", {}).get("output_tokens"), "haiku_out": t.get("haiku", {}).get("output_tokens"),
                        "function_lengths": json.dumps(x["function_lengths"]) if x["function_lengths"] else ""})
            w.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()
    config = load_json(HERE / args.config)
    results_parent = (HERE / config.get("results_dir", "results/runs")).parent
    out = pathlib.Path(args.out) if args.out else results_parent / "summary.md"
    csv_path = pathlib.Path(args.csv) if args.csv else results_parent / "runs.csv"
    rows, unpriced = collect_rows(config)
    if not rows:
        print("no completed runs")
        return
    text = render(rows, unpriced)
    out.write_text(text, encoding="utf-8")
    write_csv(rows, csv_path)
    print(text)
    print(f"\nwrote {out} and {csv_path}")


if __name__ == "__main__":
    main()
