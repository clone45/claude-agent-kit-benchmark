"""Metric extraction from a run's saved artifacts: stream-json output, transcripts, prices.

Everything here is pure: it reads files and returns dicts. run.py calls it right after a
run; summarize.py can call it again to recompute from the raw files.
"""

from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict

HAIKU_TIER_LIMIT = 100_000


def read_jsonl(path):
    out = []
    p = pathlib.Path(path)
    if not p.exists():
        return out
    with p.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def norm_model(model):
    return re.sub(r"\[1m\]$", "", model or "")


def price_table(prices, model, prompt_tokens=0):
    table = prices["usd_per_million_tokens"].get(norm_model(model))
    if table is None:
        return None
    if "over_100k_prompt" in table and prompt_tokens > HAIKU_TIER_LIMIT:
        return table["over_100k_prompt"]
    return table


def _tool_result_text(block):
    content = block.get("content")
    if isinstance(content, list):
        return " ".join(str(b.get("text", "")) for b in content if isinstance(b, dict))
    return str(content or "")


def stream_summary(events):
    """Dedupe assistant events per API response and account per model and scope."""
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    results = [e for e in events if e.get("type") == "result"]
    result = results[-1] if results else None

    seen = set()
    calls = []  # one row per API response
    main_context = []
    sub_types = defaultdict(int)
    for e in events:
        if e.get("type") != "assistant":
            continue
        msg = e.get("message") or {}
        mid = msg.get("id") or e.get("uuid")
        parent = e.get("parent_tool_use_id")
        key = (parent, mid)
        if key in seen:
            continue
        seen.add(key)
        u = msg.get("usage") or {}
        cc = u.get("cache_creation_input_tokens") or 0
        ccd = u.get("cache_creation") or {}
        c5, c1 = ccd.get("ephemeral_5m_input_tokens"), ccd.get("ephemeral_1h_input_tokens")
        if c5 is None and c1 is None:
            c5, c1 = cc, 0
        row = {
            "model": msg.get("model") or "unknown",
            "scope": "main" if parent is None else "sub",
            "subagent_type": e.get("subagent_type"),
            "input": u.get("input_tokens") or 0,
            "cache_read": u.get("cache_read_input_tokens") or 0,
            "cache_create": cc,
            "cache_create_5m": c5 or 0,
            "cache_create_1h": c1 or 0,
        }
        row["prompt_tokens"] = row["input"] + row["cache_read"] + row["cache_create"]
        calls.append(row)
        if parent is None:
            main_context.append(row["prompt_tokens"])
        else:
            sub_types[e.get("subagent_type") or "unknown"] += 1

    per_model = defaultdict(lambda: {"calls": 0, "input": 0, "cache_read": 0, "cache_create": 0,
                                     "cache_create_5m": 0, "cache_create_1h": 0, "main_calls": 0, "sub_calls": 0})
    for r in calls:
        pm = per_model[r["model"]]
        pm["calls"] += 1
        for k in ("input", "cache_read", "cache_create", "cache_create_5m", "cache_create_1h"):
            pm[k] += r[k]
        pm["main_calls" if r["scope"] == "main" else "sub_calls"] += 1

    shunt_denials = 0
    tool_errors = 0
    for e in events:
        if e.get("type") != "user":
            continue
        for blk in ((e.get("message") or {}).get("content") or []):
            if isinstance(blk, dict) and blk.get("type") == "tool_result":
                text = _tool_result_text(blk)
                if "shunt:" in text:
                    shunt_denials += 1
                if blk.get("is_error"):
                    tool_errors += 1
    permission_denied_events = sum(1 for e in events if e.get("type") == "system" and e.get("subtype") == "permission_denied")
    api_retries = [e for e in events if e.get("type") == "system" and e.get("subtype") == "api_retry"]

    return {
        "init": init,
        "result": result,
        "calls": calls,
        "per_model": dict(per_model),
        "main_api_calls": sum(1 for r in calls if r["scope"] == "main"),
        "sub_api_calls": sum(1 for r in calls if r["scope"] == "sub"),
        "sub_calls_by_type": dict(sub_types),
        "context_end_tokens": main_context[-1] if main_context else None,
        "context_max_tokens": max(main_context) if main_context else None,
        "shunt_denials": shunt_denials,
        "tool_errors": tool_errors,
        "permission_denied_events": permission_denied_events,
        "api_retries": len(api_retries),
        "api_retry_errors": sorted({str(e.get("error")) for e in api_retries}),
    }


def compute_cost(model_usage, calls, prices):
    """Input-side cost from per-call stream rows (exact tiering and TTL split); output from modelUsage.

    Falls back to modelUsage alone, assuming 5-minute cache writes, when the stream has no rows
    for a model. Returns per-model rows plus a total and a list of models with no price.
    """
    rows = {}
    unknown = []
    stream_by_model = defaultdict(lambda: {"input": 0, "cache_read": 0, "cache_create": 0, "cost_input_side": 0.0, "calls": 0})
    for r in calls:
        p = price_table(prices, r["model"], r["prompt_tokens"])
        if p is None:
            continue
        s = stream_by_model[norm_model(r["model"])]
        s["calls"] += 1
        s["input"] += r["input"]
        s["cache_read"] += r["cache_read"]
        s["cache_create"] += r["cache_create"]
        s["cost_input_side"] += (r["input"] * p["input"] + r["cache_read"] * p["cache_read"]
                                 + r["cache_create_5m"] * p["cache_write_5m"] + r["cache_create_1h"] * p["cache_write_1h"]) / 1e6

    total = 0.0
    for model, mu in (model_usage or {}).items():
        p = price_table(prices, model)
        if p is None:
            unknown.append(model)
            continue
        key = norm_model(model)
        s = stream_by_model.get(key)
        inp, cr, cc, out = (mu.get("inputTokens") or 0, mu.get("cacheReadInputTokens") or 0,
                            mu.get("cacheCreationInputTokens") or 0, mu.get("outputTokens") or 0)
        if s and s["calls"]:
            input_side = s["cost_input_side"]
            # Scale if the stream under-reports (e.g. missing events): keep the stream's tier/TTL mix.
            stream_tokens = s["input"] + s["cache_read"] + s["cache_create"]
            usage_tokens = inp + cr + cc
            scale = (usage_tokens / stream_tokens) if stream_tokens and usage_tokens else 1.0
            input_side *= scale
            basis = "stream_per_call" if abs(scale - 1.0) < 0.02 else f"stream_scaled_x{scale:.3f}"
        else:
            input_side = (inp * p["input"] + cr * p["cache_read"] + cc * p["cache_write_5m"]) / 1e6
            basis = "modelUsage_assume_5m"
        output_cost = out * p["output"] / 1e6
        cost = input_side + output_cost
        total += cost
        rows[model] = {
            "input_tokens": inp, "cache_read_tokens": cr, "cache_create_tokens": cc, "output_tokens": out,
            "thinking_tokens": mu.get("thinkingTokens"),
            "cost_input_side_usd": round(input_side, 6), "cost_output_usd": round(output_cost, 6),
            "cost_usd": round(cost, 6), "claude_cost_usd": mu.get("costUSD"), "basis": basis,
            "context_window": mu.get("contextWindow"),
        }
    return {"by_model": rows, "total_usd": round(total, 6), "unpriced_models": unknown}


def cold_start(calls, prices):
    """Cache-write cost of the main session's first API call, and how warm the cache was.

    The first call writes the system prompt and tools to the cache unless an earlier session
    on the same model left them cached, so this part of a run's cost depends on run order.
    """
    first = next((r for r in calls if r["scope"] == "main"), None)
    if first is None:
        return {"first_call_cache_create_tokens": None, "first_call_cache_read_tokens": None, "cold_write_usd": 0.0}
    p = price_table(prices, first["model"], first["prompt_tokens"])
    cost = 0.0
    if p:
        cost = (first["cache_create_5m"] * p["cache_write_5m"] + first["cache_create_1h"] * p["cache_write_1h"]) / 1e6
    return {"first_call_cache_create_tokens": first["cache_create"], "first_call_cache_read_tokens": first["cache_read"],
            "cold_write_usd": round(cost, 6)}


def transcript_summary(main_path):
    """Compaction count and deduplicated output tokens from the on-disk main transcript."""
    recs = read_jsonl(main_path)
    compactions = [r for r in recs if r.get("type") == "system" and r.get("subtype") == "compact_boundary"]
    seen = set()
    out_tokens = 0
    api_calls = 0
    models = defaultdict(int)
    for r in recs:
        if r.get("type") != "assistant":
            continue
        rid = r.get("requestId") or (r.get("message") or {}).get("id")
        if rid in seen:
            continue
        seen.add(rid)
        api_calls += 1
        u = (r.get("message") or {}).get("usage") or {}
        out_tokens += u.get("output_tokens") or 0
        models[(r.get("message") or {}).get("model") or "unknown"] += 1
    return {
        "records": len(recs),
        "compactions": len(compactions),
        "compaction_meta": [c.get("compactMetadata") for c in compactions],
        "main_api_calls": api_calls,
        "main_output_tokens": out_tokens,
        "models": dict(models),
    }


VERDICT_RE = re.compile(r"Verdict:\**\s*\**\s*(PASS|FAIL)", re.I)


def subagent_summary(subagents_dir):
    """One row per subagent transcript: type, model, call count, refuter verdict if any."""
    rows = []
    d = pathlib.Path(subagents_dir)
    if not d.exists():
        return rows
    for jl in sorted(d.glob("agent-*.jsonl")):
        meta_path = jl.with_suffix(".meta.json")
        meta = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                meta = {}
        recs = read_jsonl(jl)
        seen = set()
        calls = 0
        models = defaultdict(int)
        last_text = ""
        for r in recs:
            if r.get("type") != "assistant":
                continue
            msg = r.get("message") or {}
            rid = r.get("requestId") or msg.get("id")
            if rid not in seen:
                seen.add(rid)
                calls += 1
                models[msg.get("model") or "unknown"] += 1
            for blk in msg.get("content") or []:
                if isinstance(blk, dict) and blk.get("type") == "text":
                    last_text = blk.get("text") or last_text
        verdict = None
        agent_type = meta.get("agentType") or ""
        if "refuter" in agent_type.lower():
            m = VERDICT_RE.search(last_text)
            verdict = m.group(1).upper() if m else "UNKNOWN"
        rows.append({
            "file": jl.name,
            "agent_type": agent_type,
            "meta_model": meta.get("model"),
            "api_calls": calls,
            "models": dict(models),
            "refuter_verdict": verdict,
        })
    return rows


def rework_stats(sub_rows):
    refuters = [r for r in sub_rows if r["refuter_verdict"] is not None]
    fails = sum(1 for r in refuters if r["refuter_verdict"] == "FAIL")
    builders = sum(1 for r in sub_rows if "builder" in (r["agent_type"] or "").lower())
    return {"refuter_runs": len(refuters), "refuter_fail": fails, "builder_runs": builders,
            "refuter_verdicts": [r["refuter_verdict"] for r in refuters]}
