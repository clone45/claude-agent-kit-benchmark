#!/usr/bin/env python3
"""Build results/report.html: a one-page executive report over one or more phases.

usage: report.py --config config.json --config config2.json [--out results/report.html]
Each config contributes a phase (its own runs, tasks, and report name). Re-run after more runs complete.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "lib"))
import summarize  # noqa: E402


def load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def collect_phase(config_path):
    config = load_json(HERE / config_path)
    tasks_doc = load_json(HERE / config.get("tasks_file", "tasks.json"))
    results_dir = HERE / config.get("results_dir", "results/runs")
    rows, unpriced = summarize.collect_rows(config)
    versions, dates = set(), []
    runs = []
    for row in rows:
        r = load_json(results_dir / row["run_id"] / "run.json")
        init = load_json(results_dir / row["run_id"] / "init.json") if (results_dir / row["run_id"] / "init.json").exists() else {}
        versions.add(init.get("claude_code_version") or "")
        dates.append(r["process"]["started_at"][:10])
        opus = row["tokens"].get("opus", {})
        runs.append({
            "run": row["run_id"][:8], "task": row["task"], "type": row["type"], "condition": row["condition"], "mode": row["mode"], "chain_step": row["chain_step"],
            "subtype": row["subtype"], "cost": row["cost_usd"], "cost_warm": row["cost_warm_usd"], "wall_s": row["wall_s"], "turns": row["turns"],
            "main_calls": row["main_api_calls"], "sub_calls": row["sub_api_calls"], "subagents": row["subagents"],
            "context_end": row["context_end_tokens"], "context_max": row["context_max_tokens"], "context_window": r.get("context_window"),
            "compactions": row["compactions"], "shunt": row["shunt_denials"], "refuter_fail": row["refuter_fail"], "builder_runs": row["builder_runs"],
            "hidden_pass": row["hidden_pass"], "full_pass": row["full_pass"], "lint_pass": row["lint_pass"], "no_changes": row["no_changes"], "all_pass": row["all_pass"],
            "first_cache_create": row["first_call_cache_create"], "opus_in": opus.get("input_tokens", 0), "opus_cache_read": opus.get("cache_read_tokens", 0),
            "opus_cache_create": opus.get("cache_create_tokens", 0), "opus_out": opus.get("output_tokens", 0),
            "cost_opus": row["cost_opus"], "cost_sonnet": row["cost_sonnet"], "cost_haiku": row["cost_haiku"], "grade": row["grade"],
            "diff_files": len(r.get("diff", {}).get("files_changed") or []), "function_lengths": row["function_lengths"],
        })
    rep = config.get("report", {})
    return {
        "name": rep.get("name", config_path), "subtitle": rep.get("subtitle", ""),
        "run_dates": sorted(set(dates)), "claude_versions": sorted(v for v in versions if v),
        "base_commit": tasks_doc.get("base_commit"), "plugin_commit": tasks_doc.get("plugin_commit"),
        "tasks": [{"label": t["label"], "type": t["type"], "length": t["length"]} for t in tasks_doc["tasks"]],
        "chain_order": tasks_doc.get("chain_order"), "n_tasks_planned": len(tasks_doc["tasks"]), "unpriced": unpriced, "runs": runs,
    }


TEMPLATE = r"""<title>Agent Kit versus Plain Opus</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100,500;100,700;112,700&family=Source+Sans+3:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: one narrow column (max 820px). Bottom line first, then one block per phase: verdict, four figures, one chart, three findings,
   details folded away. Two validated condition hues carry identity everywhere; status hues are reserved for pass/fail. */
:root {
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --grid: #e1e0d9; --axis: #c3c2b7; --ring: rgba(11,11,11,0.10);
  --cond-a: #2a78d6; --cond-b: #eb6834;
  --good: #0ca30c; --good-text: #006300; --bad: #d03b3b; --warn-text: #7a4a00; --warn-bg: rgba(250,178,25,0.18);
  --font-display: "Archivo", "Helvetica Neue", Arial, sans-serif;
  --font-body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7; --muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
    --cond-a: #3987e5; --cond-b: #d95926; --good: #0ca30c; --good-text: #0ca30c; --bad: #d03b3b; --warn-text: #fab219; --warn-bg: rgba(250,178,25,0.14);
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --page: #0d0d0d; --surface: #1a1a19; --ink: #f0efec; --ink-2: #c3c2b7; --muted: #898781;
  --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
  --cond-a: #3987e5; --cond-b: #d95926; --good: #0ca30c; --good-text: #0ca30c; --bad: #d03b3b; --warn-text: #fab219; --warn-bg: rgba(250,178,25,0.14);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--page); color: var(--ink); font-family: var(--font-body); font-size: 17px; line-height: 1.45;
  padding-block: 32px 56px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.wrap { max-width: 820px; margin: 0 auto; display: grid; gap: 30px; }
h1, h2, h3 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.1; }
h1 { font-size: clamp(30px, 5vw, 44px); font-weight: 700; font-stretch: 112%; letter-spacing: -0.01em; }
h2 { font-size: 24px; font-weight: 700; }
h3 { font-size: 17px; font-weight: 700; }
p { margin: 0; }
.eyebrow { font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-2); }
header { display: grid; gap: 10px; }
.question { font-size: 19px; color: var(--ink-2); max-width: 62ch; }
.verdict { display: grid; gap: 8px; padding: 16px 18px; border-left: 4px solid var(--ink); background: var(--surface); border-radius: 0 6px 6px 0; }
.chip { display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; padding: 3px 8px; border-radius: 999px; width: max-content; }
.chip.early { background: var(--warn-bg); color: var(--warn-text); }
.chip.same { background: var(--grid); color: var(--ink-2); }
.chip.diff { background: var(--ring); color: var(--ink); }
.verdict .headline { font-family: var(--font-display); font-size: 21px; font-weight: 700; line-height: 1.25; text-wrap: balance; }
.verdict .detail { color: var(--ink-2); font-size: 16px; }
.bottom { border-left-color: var(--cond-b); }
.bottom ul { margin: 0; padding-left: 18px; display: grid; gap: 6px; font-size: 16px; }
.phase { display: grid; gap: 16px; padding-top: 10px; border-top: 1px solid var(--axis); }
.phase .sub { color: var(--ink-2); max-width: 66ch; }
.legend { display: flex; flex-wrap: wrap; gap: 8px 20px; font-size: 15px; color: var(--ink-2); align-items: center; }
.key { display: inline-flex; align-items: center; gap: 8px; }
.key i { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.key.a i { background: var(--cond-a); } .key.b i { background: var(--cond-b); }
.key b { font-weight: 600; color: var(--ink); }
.modehead { font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink-2); margin-top: 4px; }
.figures { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 180px), 1fr)); gap: 12px; }
.fig { background: var(--surface); border: 1px solid var(--ring); border-radius: 6px; padding: 14px 16px 12px; display: grid; gap: 10px; align-content: start; }
.fig .label { font-size: 14px; color: var(--ink-2); line-height: 1.3; }
.fig .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.fig .cond { display: flex; align-items: center; gap: 6px; font-size: 12px; font-family: var(--font-mono); color: var(--ink-2); }
.fig .cond i { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
.fig .cond.a i { background: var(--cond-a); } .fig .cond.b i { background: var(--cond-b); }
.fig .value { font-weight: 600; font-size: 28px; line-height: 1.05; letter-spacing: -0.01em; margin-top: 4px; }
.fig .change { font-size: 14px; color: var(--ink-2); border-top: 1px solid var(--grid); padding-top: 8px; }
.fig .change b { color: var(--ink); font-weight: 600; }
.chart { background: var(--surface); border: 1px solid var(--ring); border-radius: 6px; padding: 16px 18px 10px; display: grid; gap: 8px; position: relative; }
.chart .title { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 16px; align-items: baseline; }
.chart .title span { font-size: 14px; color: var(--muted); }
.chart svg { width: 100%; height: auto; display: block; overflow: visible; }
.chart text { font-family: var(--font-body); font-size: 13px; fill: var(--ink-2); }
.chart text.tick { fill: var(--muted); font-variant-numeric: tabular-nums; }
.chart text.row { fill: var(--ink); font-weight: 600; font-size: 14px; }
.chart text.rowtype { fill: var(--muted); font-size: 12px; }
.chart text.val { fill: var(--ink); font-variant-numeric: tabular-nums; }
.chart line.grid { stroke: var(--grid); stroke-width: 1; }
.chart line.axis { stroke: var(--axis); stroke-width: 1; }
.bar.a { fill: var(--cond-a); } .bar.b { fill: var(--cond-b); }
.range { stroke: var(--ink); stroke-width: 1.5; opacity: 0.6; }
.hit { fill: transparent; }
.hit:hover + .bar, .hit:focus-visible + .bar { opacity: 0.8; }
.hit:focus { outline: none; }
.tooltip { position: absolute; pointer-events: none; background: var(--ink); color: var(--page); font-size: 13px; line-height: 1.35; padding: 8px 10px; border-radius: 4px; max-width: 250px; z-index: 5; display: none; }
.tooltip b { font-size: 15px; display: block; margin-bottom: 2px; font-variant-numeric: tabular-nums; }
.findings { display: grid; gap: 10px; }
.finding { display: grid; grid-template-columns: 28px 1fr; gap: 10px; align-items: start; font-size: 17px; }
.finding .n { font-family: var(--font-mono); font-size: 13px; color: var(--muted); padding-top: 4px; }
.finding b { font-weight: 600; }
details { background: var(--surface); border: 1px solid var(--ring); border-radius: 6px; }
summary { cursor: pointer; padding: 14px 18px; font-family: var(--font-display); font-weight: 700; font-size: 16px; list-style: none; display: flex; justify-content: space-between; align-items: center; }
summary::-webkit-details-marker { display: none; }
summary::after { content: "Show"; font-family: var(--font-mono); font-size: 12px; color: var(--ink-2); letter-spacing: 0.06em; text-transform: uppercase; }
details[open] summary::after { content: "Hide"; }
details > .inner { padding: 4px 18px 18px; display: grid; gap: 22px; border-top: 1px solid var(--grid); }
details h3 { font-size: 15px; margin-top: 14px; }
.table-wrap { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
thead th { text-align: left; font-weight: 600; font-size: 12px; color: var(--ink-2); letter-spacing: 0.03em; text-transform: uppercase; border-bottom: 1px solid var(--axis); padding: 7px 8px; white-space: nowrap; }
tbody td { padding: 7px 8px; border-bottom: 1px solid var(--grid); vertical-align: top; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
td.mono { font-family: var(--font-mono); font-size: 12.5px; }
.cnd { display: inline-flex; align-items: center; gap: 6px; font-weight: 600; }
.cnd i { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
.cnd.a i { background: var(--cond-a); } .cnd.b i { background: var(--cond-b); }
.status { display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; }
.status i { width: 8px; height: 8px; display: inline-block; border-radius: 2px; }
.status.pass { color: var(--good-text); } .status.pass i { background: var(--good); }
.status.fail { color: var(--bad); } .status.fail i { background: var(--bad); }
.status.na { color: var(--muted); } .status.na i { background: var(--axis); }
details ul { margin: 0; padding-left: 18px; display: grid; gap: 6px; font-size: 15px; }
code { font-family: var(--font-mono); font-size: 0.86em; background: var(--page); border: 1px solid var(--grid); border-radius: 3px; padding: 0 4px; }
footer { font-size: 13px; color: var(--muted); font-family: var(--font-mono); }
@media (max-width: 560px) { body { font-size: 16px; } .fig .value { font-size: 24px; } .finding { font-size: 16px; } }
@media (prefers-reduced-motion: no-preference) { .bar { transition: opacity 120ms ease; } }
</style>

<div class="wrap">
  <header>
    <div class="eyebrow" id="eyebrow"></div>
    <h1>Agent Kit versus Plain Opus</h1>
    <p class="question">Does the claude-agent-kit plugin make a Claude Code task cheaper, better, or faster than a plain Opus session?</p>
  </header>
  <div class="verdict bottom" id="bottom"></div>
  <div class="legend">
    <span class="key a"><i></i><b>A</b> plain Opus session</span>
    <span class="key b"><i></i><b>B</b> same session with the plugin</span>
  </div>
  <div id="phases"></div>
  <details>
    <summary>How this was measured</summary>
    <div class="inner" id="method"></div>
  </details>
  <footer id="footer"></footer>
</div>
<div class="tooltip" id="tooltip" role="status" aria-live="polite"></div>

<script id="data" type="application/json">__DATA__</script>
<script>
(function () {
  const DATA = JSON.parse(document.getElementById('data').textContent);
  const TYPE_NAME = { bugfix: 'Bug fix', feature: 'Small feature', refactor: 'Refactor', find: 'Find where', long: 'Long task' };
  const MODE_NAME = { fresh: 'Fresh sessions, one task each', chain: 'One continued session, tasks in sequence' };
  const fmtUSD = v => v == null ? 'n/a' : '$' + v.toFixed(2);
  const fmtUSD3 = v => v == null ? 'n/a' : '$' + v.toFixed(3);
  const fmtInt = v => v == null ? 'n/a' : Math.round(v).toLocaleString('en-US');
  const fmtK = v => v == null ? 'n/a' : (v >= 1000 ? (v / 1000).toFixed(v >= 10000 ? 0 : 1) + 'K' : String(Math.round(v)));
  const fmtS = v => v == null ? 'n/a' : (v >= 120 ? (v / 60).toFixed(1) + ' min' : Math.round(v) + ' s');
  const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
  const stdev = a => a.length > 1 ? Math.sqrt(a.map(x => (x - mean(a)) ** 2).reduce((x, y) => x + y, 0) / (a.length - 1)) : 0;
  const nums = (arr, k) => arr.map(r => r[k]).filter(v => typeof v === 'number');
  const el = (tag, attrs, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs || {})) { if (k === 'class') e.className = v; else if (k === 'text') e.textContent = v; else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; };
  const svgEl = (tag, attrs) => { const e = document.createElementNS('http://www.w3.org/2000/svg', tag); for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v); return e; };
  const passRate = arr => { const v = arr.map(r => r.all_pass).filter(x => x !== null && x !== undefined); return v.length ? v.filter(Boolean).length / v.length : null; };
  const pct = v => v == null ? 'n/a' : Math.round(v * 100) + '%';
  const pctWord = x => x == null ? 'about the same' : `${Math.abs(Math.round(x * 100))}% ${x >= 0 ? 'more' : 'less'}`;
  const tooltip = document.getElementById('tooltip');
  const showTip = (card, evt, rows) => { tooltip.replaceChildren(...rows); tooltip.style.display = 'block'; const r = card.getBoundingClientRect(); tooltip.style.left = Math.min(evt.clientX - r.left + 14, r.width - 260) + 'px'; tooltip.style.top = (evt.clientY - r.top + 14) + 'px'; card.appendChild(tooltip); };
  const hideTip = () => { tooltip.style.display = 'none'; };

  function summary(runs) {
    const A = runs.filter(r => r.condition === 'A'), B = runs.filter(r => r.condition === 'B');
    const cA = mean(nums(A, 'cost')), cB = mean(nums(B, 'cost'));
    const perCell = {}; runs.forEach(r => { const k = r.task + r.condition + r.mode; perCell[k] = (perCell[k] || 0) + 1; });
    const minCell = runs.length ? Math.min(...Object.values(perCell)) : 0;
    const pooled = Math.sqrt(((stdev(nums(A, 'cost')) ** 2) + (stdev(nums(B, 'cost')) ** 2)) / 2);
    return { A, B, cA, cB, costChange: cA ? (cB - cA) / cA : null, pA: passRate(A), pB: passRate(B),
      tA: mean(nums(A, 'wall_s')), tB: mean(nums(B, 'wall_s')), xA: mean(nums(A, 'context_end')), xB: mean(nums(B, 'context_end')),
      minCell, separated: minCell > 1 && cA != null && cB != null && Math.abs(cB - cA) > pooled,
      subB: nums(B, 'sub_calls').reduce((p, q) => p + q, 0), shuntB: nums(B, 'shunt').reduce((p, q) => p + q, 0), refFail: nums(B, 'refuter_fail').reduce((p, q) => p + q, 0),
      tasks: new Set(runs.map(r => r.task)).size };
  }

  function figures(root, runs) {
    const s = summary(runs);
    const grid = el('div', { class: 'figures' });
    const change = (a, b, unit) => { if (a == null || b == null) return 'n/a'; if (a === b) return 'same'; if (unit === 'pp') return `${b > a ? '+' : '−'}${Math.abs(Math.round((b - a) * 100))} points`; const r = (b - a) / a; return `${r > 0 ? '+' : '−'}${Math.abs(Math.round(r * 100))}%`; };
    const fig = (label, aV, bV, chg, tail) => grid.append(el('div', { class: 'fig' }, el('div', { class: 'label', text: label }),
      el('div', { class: 'pair' }, el('div', {}, el('div', { class: 'cond a' }, el('i'), 'A'), el('div', { class: 'value', text: aV })), el('div', {}, el('div', { class: 'cond b' }, el('i'), 'B'), el('div', { class: 'value', text: bV }))),
      el('div', { class: 'change' }, 'B vs A: ', el('b', { text: chg }), tail ? ' ' + tail : '')));
    fig('Cost per task (list price)', fmtUSD(s.cA), fmtUSD(s.cB), change(s.cA, s.cB), '');
    fig('Tasks passing every check', pct(s.pA), pct(s.pB), change(s.pA, s.pB, 'pp'), '');
    fig('Time per task', fmtS(s.tA), fmtS(s.tB), change(s.tA, s.tB), '');
    fig('Context at the end, tokens', fmtK(s.xA), fmtK(s.xB), change(s.xA, s.xB), 'of a 1M window');
    root.append(grid);
  }

  function barChart(root, runs, title, note, taskOrder, taskType) {
    const card = el('div', { class: 'chart' });
    card.append(el('div', { class: 'title' }, el('h3', { text: title }), el('span', { text: note })));
    const W = 820, left = 110, right = 70, rowH = 46, barH = 14, top = 24, bottom = 30;
    const H = top + rowH * taskOrder.length + bottom;
    const maxV = Math.max(...nums(runs, 'cost'), 0.01);
    const step = (() => { const raw = maxV / 4; const p = Math.pow(10, Math.floor(Math.log10(raw))); for (const m of [1, 2, 2.5, 5, 10]) if (m * p >= raw) return m * p; return 10 * p; })();
    const xmax = Math.ceil(maxV / step) * step;
    const x = v => left + (v / xmax) * (W - left - right);
    const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': title });
    for (let t = 0; t <= xmax + 1e-9; t += step) {
      svg.append(svgEl('line', { class: 'grid', x1: x(t), x2: x(t), y1: top - 4, y2: H - bottom + 2 }));
      const tx = svgEl('text', { class: 'tick', x: x(t), y: H - bottom + 18, 'text-anchor': 'middle' }); tx.textContent = '$' + t.toFixed(2); svg.append(tx);
    }
    svg.append(svgEl('line', { class: 'axis', x1: left, x2: left, y1: top - 4, y2: H - bottom + 2 }));
    taskOrder.forEach((task, i) => {
      const y0 = top + rowH * i;
      const lab = svgEl('text', { class: 'row', x: left - 12, y: y0 + rowH / 2 - 2, 'text-anchor': 'end' }); lab.textContent = task; svg.append(lab);
      const typ = svgEl('text', { class: 'rowtype', x: left - 12, y: y0 + rowH / 2 + 13, 'text-anchor': 'end' }); typ.textContent = TYPE_NAME[taskType[task]] || ''; svg.append(typ);
      ['A', 'B'].forEach((c, ci) => {
        const rs = runs.filter(r => r.task === task && r.condition === c); const vals = nums(rs, 'cost'); if (!vals.length) return;
        const m = mean(vals), lo = Math.min(...vals), hi = Math.max(...vals);
        const y = y0 + 7 + ci * (barH + 2); const w = Math.max(x(m) - left, 0);
        const hit = svgEl('rect', { class: 'hit', x: left, y: y - 2, width: W - left - right, height: barH + 4, tabindex: 0, role: 'img', 'aria-label': `${task} ${c}: ${fmtUSD(m)}` });
        const bar = svgEl('path', { class: 'bar ' + c.toLowerCase(), d: `M${left},${y} H${left + Math.max(w - 4, 0)} a4,4 0 0 1 4,4 V${y + barH - 4} a4,4 0 0 1 -4,4 H${left} Z` });
        const rows = () => [el('b', { text: fmtUSD(m) + (vals.length > 1 ? ' mean' : '') }), el('div', { text: `${task} · condition ${c} · ${vals.length} run${vals.length === 1 ? '' : 's'}` }), vals.length > 1 ? el('div', { text: `lowest ${fmtUSD(lo)}, highest ${fmtUSD(hi)}` }) : null, el('div', { text: `checks: ${rs.filter(r => r.all_pass).length} of ${rs.filter(r => r.all_pass !== null).length} passed` })];
        hit.addEventListener('pointermove', e => showTip(card, e, rows())); hit.addEventListener('pointerleave', hideTip);
        hit.addEventListener('focus', () => { const b = hit.getBoundingClientRect(); showTip(card, { clientX: b.left + 8, clientY: b.top + 8 }, rows()); }); hit.addEventListener('blur', hideTip);
        svg.append(hit, bar);
        if (vals.length > 1) svg.append(svgEl('line', { class: 'range', x1: x(lo), x2: x(hi), y1: y + barH / 2, y2: y + barH / 2 }));
        const vl = svgEl('text', { class: 'val', x: x(vals.length > 1 ? hi : m) + 8, y: y + barH / 2 + 4 }); vl.textContent = fmtUSD(m); svg.append(vl);
      });
      if (i > 0) svg.append(svgEl('line', { class: 'grid', x1: left, x2: W - right + 8, y1: y0, y2: y0 }));
    });
    card.append(svg);
    root.append(card);
  }

  function findings(root, runs, s) {
    const f = el('section', { class: 'findings' });
    const add = (n, strong, rest) => f.append(el('div', { class: 'finding' }, el('div', { class: 'n', text: n }), el('div', {}, el('b', { text: strong }), ' ' + rest)));
    const runsB = s.B.length, withSub = s.B.filter(r => r.sub_calls > 0).length;
    if (runsB) {
      if (s.subB === 0) add('1', 'The plugin never delegated.', `In all ${runsB} B runs the main session did the work itself: 0 calls to the plugin's agents and ${s.shuntB} reads blocked by its hook.`);
      else add('1', `The plugin delegated in ${withSub} of ${runsB} B runs.`, `${fmtInt(s.subB)} subagent API calls in total, ${s.shuntB} reads blocked by the read-limit hook, ${s.refFail} review rejections sent back for rework.`);
    }
    const ctxDiff = (s.xA != null && s.xB != null) ? s.xB - s.xA : null;
    add('2', ctxDiff != null && ctxDiff > 0 ? 'The plugin added context rather than saving it.' : 'The plugin carried less context.', `B's main session ended with ${fmtInt(Math.abs(ctxDiff || 0))} ${ctxDiff >= 0 ? 'more' : 'fewer'} tokens in context on average. The largest context seen was ${fmtK(Math.max(...nums(runs, 'context_max'), 0))} tokens of a 1M window; ${nums(runs, 'compactions').reduce((p, q) => p + q, 0)} compactions occurred.`);
    const allPass = runs.filter(r => r.all_pass).length, checkable = runs.filter(r => r.all_pass !== null && r.all_pass !== undefined).length;
    const failA = s.A.filter(r => r.all_pass === false).length, failB = s.B.filter(r => r.all_pass === false).length;
    add('3', `${allPass} of ${checkable} runs passed every automatic check.`, `${failA} failures in A, ${failB} in B. Time per task ${s.tA && s.tB ? `differed by ${fmtS(Math.abs(s.tB - s.tA))} on average` : 'is not comparable yet'}.`);
    root.append(f);
  }

  function verdictBox(s, scopeWords) {
    const box = el('div', { class: 'verdict' });
    const qualityWord = (s.pA === s.pB) ? 'the same pass rate' : `a pass rate of ${pct(s.pB)} against ${pct(s.pA)}`;
    let chip, headline, detail;
    if (!s.A.length || !s.B.length) { chip = el('span', { class: 'chip early', text: 'No data yet' }); headline = 'Runs have not completed for both conditions.'; detail = ''; }
    else if (s.minCell < 2) { chip = el('span', { class: 'chip early', text: 'Too early to call' }); headline = `So far the plugin costs ${pctWord(s.costChange)} per task, with ${qualityWord}.`; detail = `One run per task and condition${scopeWords}. Model output varies between runs, so this needs the planned repetitions before it means anything.`; }
    else if (!s.separated) { chip = el('span', { class: 'chip same', text: 'No measurable cost difference' }); headline = `The plugin changes cost by ${pctWord(s.costChange)} per task, within the run-to-run spread, with ${qualityWord}.`; detail = `${s.minCell} runs per task and condition across ${s.tasks} tasks${scopeWords}. The cost difference is smaller than the variation between repeated runs of the same task.`; }
    else { chip = el('span', { class: 'chip diff', text: s.costChange > 0 ? 'Plugin costs more' : 'Plugin costs less' }); headline = `The plugin costs ${pctWord(s.costChange)} per task, with ${qualityWord}.`; detail = `${s.minCell} runs per task and condition across ${s.tasks} tasks${scopeWords}. The difference is larger than the run-to-run spread.`; }
    box.append(chip, el('div', { class: 'headline', text: headline }), el('div', { class: 'detail', text: detail }));
    return box;
  }

  function table(headers, rowsEls) { const t = el('table'); const tr = el('tr'); headers.forEach(h => tr.append(el('th', { class: h.num ? 'num' : '', text: h.label }))); t.append(el('thead', {}, tr)); const tb = el('tbody'); rowsEls.forEach(r => tb.append(r)); t.append(tb); return el('div', { class: 'table-wrap' }, t); }
  const cnd = c => el('span', { class: 'cnd ' + c.toLowerCase() }, el('i'), c);
  const status = s => s == null ? el('span', { class: 'status na' }, el('i'), 'n/a') : (s ? el('span', { class: 'status pass' }, el('i'), 'pass') : el('span', { class: 'status fail' }, el('i'), 'fail'));

  function phaseDetails(root, phase, taskOrder) {
    const d = el('details'); d.append(el('summary', { text: 'Every run in ' + phase.name }));
    const inner = el('div', { class: 'inner' });
    const modes = [...new Set(phase.runs.map(r => r.mode))];
    modes.forEach(mode => {
      const rs = phase.runs.filter(r => r.mode === mode);
      const tRows = [];
      [['all', rs]].concat(['bugfix', 'feature', 'refactor', 'find', 'long'].map(t => [t, rs.filter(r => r.type === t)]).filter(([, x]) => x.length)).forEach(([t, sub]) => ['A', 'B'].forEach(c => {
        const q = sub.filter(r => r.condition === c); if (!q.length) return;
        const rng = (a, fm) => a.length > 1 ? ` (${fm(Math.min(...a))} to ${fm(Math.max(...a))})` : '';
        const cost = nums(q, 'cost'), wall = nums(q, 'wall_s'), ctx = nums(q, 'context_end');
        const tr = el('tr'); tr.append(el('td', { text: t === 'all' ? 'All types' : TYPE_NAME[t] }), el('td', {}, cnd(c)), el('td', { class: 'num', text: String(q.length) }),
          el('td', { class: 'num', text: fmtUSD(mean(cost)) + rng(cost, fmtUSD) }), el('td', { class: 'num', text: fmtS(mean(wall)) + rng(wall, fmtS) }), el('td', { class: 'num', text: fmtInt(mean(ctx)) }),
          el('td', { class: 'num', text: pct(passRate(q)) }), el('td', { class: 'num', text: fmtInt(nums(q, 'sub_calls').reduce((p1, q1) => p1 + q1, 0)) }), el('td', { class: 'num', text: fmtInt(nums(q, 'shunt').reduce((p1, q1) => p1 + q1, 0)) }));
        tRows.push(tr);
      }));
      inner.append(el('h3', { text: 'By task type, ' + (MODE_NAME[mode] || mode).toLowerCase() }), table([{ label: 'Type' }, { label: 'Cond.' }, { label: 'Runs', num: true }, { label: 'Cost per task', num: true }, { label: 'Time', num: true }, { label: 'Context at end', num: true }, { label: 'All checks pass', num: true }, { label: 'Subagent calls', num: true }, { label: 'Hook denials', num: true }], tRows));
    });
    const sorted = [...phase.runs].sort((p1, q1) => (p1.mode > q1.mode) - (p1.mode < q1.mode) || taskOrder.indexOf(p1.task) - taskOrder.indexOf(q1.task) || p1.condition.localeCompare(q1.condition));
    inner.append(el('h3', { text: 'Every run' }), table([{ label: 'Task' }, { label: 'Mode' }, { label: 'Cond.' }, { label: 'Run' }, { label: 'Cost', num: true }, { label: 'Time', num: true }, { label: 'Turns', num: true }, { label: 'API calls', num: true }, { label: 'Subagent calls', num: true }, { label: 'Context at end', num: true }, { label: 'Hidden tests' }, { label: 'Suite / tests' }, { label: 'Lint, types, compile' }, { label: 'No changes' }, { label: 'Grade', num: true }],
      sorted.map(r => { const tr = el('tr'); tr.append(el('td', { text: r.task }), el('td', { text: r.mode + (r.chain_step != null ? ' ' + (r.chain_step + 1) : '') }), el('td', {}, cnd(r.condition)), el('td', { class: 'mono', text: r.run }), el('td', { class: 'num', text: fmtUSD3(r.cost) }), el('td', { class: 'num', text: fmtS(r.wall_s) }), el('td', { class: 'num', text: String(r.turns) }), el('td', { class: 'num', text: String(r.main_calls) }), el('td', { class: 'num', text: String(r.sub_calls) }), el('td', { class: 'num', text: fmtInt(r.context_end) }), el('td', {}, status(r.hidden_pass)), el('td', {}, status(r.full_pass)), el('td', {}, status(r.lint_pass)), el('td', {}, status(r.no_changes)), el('td', { class: 'num', text: r.grade == null ? 'not yet' : String(r.grade) })); return tr; })));
    d.append(inner); root.append(d);
  }

  function renderPhase(phase) {
    const root = el('section', { class: 'phase' });
    const runs = phase.runs;
    const taskType = Object.fromEntries(phase.tasks.map(t => [t.label, t.type]));
    const taskOrder = phase.tasks.map(t => t.label).filter(l => runs.some(r => r.task === l));
    root.append(el('h2', { text: phase.name }), el('p', { class: 'sub', text: phase.subtitle }));
    root.append(el('div', { class: 'eyebrow', text: `${runs.length} runs · ${taskOrder.length} of ${phase.n_tasks_planned} tasks · ${phase.run_dates.join(', ')}` }));
    const s = summary(runs);
    root.append(verdictBox(s, ''));
    const modes = [...new Set(runs.map(r => r.mode))];
    modes.forEach(mode => {
      const rs = runs.filter(r => r.mode === mode);
      if (modes.length > 1) root.append(el('div', { class: 'modehead', text: MODE_NAME[mode] || mode }));
      figures(root, rs);
      barChart(root, rs, 'Cost per task' + (modes.length > 1 ? ', ' + (mode === 'chain' ? 'chained' : 'fresh') : ''), summary(rs).minCell > 1 ? 'bar: mean of the runs · line: lowest to highest run' : 'one run each', taskOrder, taskType);
    });
    findings(root, runs, s);
    phaseDetails(root, phase, taskOrder);
    return { root, s };
  }

  // Render
  const allRuns = DATA.phases.flatMap(p => p.runs);
  const container = document.getElementById('phases');
  const phaseSummaries = [];
  DATA.phases.forEach(p => { const { root, s } = renderPhase(p); container.append(root); phaseSummaries.push([p, s]); });
  document.getElementById('eyebrow').textContent = `${allRuns.length} runs across ${DATA.phases.length} phase${DATA.phases.length === 1 ? '' : 's'} · ${[...new Set(allRuns.map(r => r.mode))].join(' and ')} sessions · generated ${DATA.generated}`;
  const bottom = document.getElementById('bottom');
  bottom.append(el('span', { class: 'chip diff', text: 'Bottom line' }));
  const ul = el('ul');
  phaseSummaries.forEach(([p, s]) => {
    if (!s.A.length || !s.B.length) { ul.append(el('li', { text: `${p.name}: no completed runs for both conditions yet.` })); return; }
    const q = (s.pA === s.pB) ? 'the same pass rate' : `pass rates of ${pct(s.pB)} (B) against ${pct(s.pA)} (A)`;
    const sep = s.minCell < 2 ? 'one run per cell so far' : (s.separated ? 'larger than the run-to-run spread' : 'within the run-to-run spread');
    const deleg = s.subB === 0 ? 'the plugin never delegated' : `the plugin delegated ${fmtInt(s.subB)} subagent calls`;
    ul.append(el('li', { text: `${p.name}: the plugin cost ${pctWord(s.costChange)} per task (${sep}) with ${q}; ${deleg}.` }));
  });
  bottom.append(ul);
  const m = document.getElementById('method');
  const li = kids => { const l = el('li'); l.append(...(Array.isArray(kids) ? kids : [kids])); return l; };
  const code = t => el('code', { text: t });
  m.append(el('h3', { text: 'Setup' }), el('ul', {},
    li(['Both conditions: ', code('claude -p'), ' on claude-opus-5-5 at effort high, bypass-permissions mode, user settings and MCP servers excluded, Claude Code ' + [...new Set(DATA.phases.flatMap(p => p.claude_versions))].join(', ') + '. Same base commit, same prompt per task. The repo is reset before every fresh run and the auto-memory folder is cleared.']),
    li('A: no plugin. CLAUDE.md holds the project notes, the check commands, and the rules.'),
    li(['B: the plugin loaded for the session with ', code('--plugin-dir'), ' plus its Agent contract appended to CLAUDE.md. Its SessionStart hook injects the orchestration rules; its PreToolUse hook denies reads over 350 lines. One change to the plugin copy: the hook also fires on forked sessions.']),
    li('Chained sessions: the tasks run in order inside one continued session; the harness commits a checkpoint after each task so every task is diffed and checked on its own, and the next task continues from that state.'),
    li('Cost: input, cache-read and cache-write tokens priced per model and cache TTL for each API call; output tokens from the final usage record (in chains, the difference between consecutive cumulative records). The runs use a claude.ai Max login; nothing was billed. Figures are list-price estimates.'),
    li('Quality: hidden tests held back from the task and copied in after the run, the project\'s own test suite or standalone tests, lint, type or compile checks, and a diff saved under a random id for blind grading.')));
  DATA.phases.forEach(p => m.append(el('h3', { text: p.name }), el('ul', {}, li(`${p.n_tasks_planned} tasks: ${['bugfix', 'feature', 'refactor', 'find', 'long'].map(t => `${p.tasks.filter(x => x.type === t).length} ${TYPE_NAME[t].toLowerCase()}`).filter(s => !s.startsWith('0 ')).join(', ')}. Base commit ${(p.base_commit || '').slice(0, 7)}; plugin commit ${(p.plugin_commit || '').slice(0, 7)}.${p.chain_order ? ' Chain order: ' + p.chain_order.join(', ') + '.' : ''}`))));
  document.getElementById('footer').textContent = `Generated ${DATA.generated} · harness: /mnt/c/Code/routing_test`;
})();
</script>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", action="append", default=None)
    ap.add_argument("--out", default=str(HERE / "results" / "report.html"))
    args = ap.parse_args()
    configs = args.config or ["config.json"]
    data = {"generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), "phases": [collect_phase(c) for c in configs]}
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    pathlib.Path(args.out).write_text(TEMPLATE.replace("__DATA__", payload), encoding="utf-8")
    print(f"wrote {args.out}: " + ", ".join(f"{p['name']} {len(p['runs'])} runs" for p in data["phases"]))


if __name__ == "__main__":
    main()
