#!/usr/bin/env python3
"""Build the test repo and one base commit per task and condition.

usage: make_tasks.py [--rebuild] [--verify]

Reads config.json and task_specs.json. Produces:
  <repo_dir>              a fresh git repo: click at the base commit, CHANGES.md removed,
                          .venv (gitignored) with click installed editable plus the check tools
  branches t-<task-uuid>-a / -b   the task's starting tree with CLAUDE.md for condition A or B
  tasks/hidden/<task-uuid>/...    HEAD copies of the hidden test files for that task
  tasks.json              resolved tasks: ids, labels, prompts, branches, hidden tests, checks
--verify runs the full suite on each task base (must pass) and the hidden tests (must fail).
"""

from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import subprocess
import sys
import uuid

HERE = pathlib.Path(__file__).resolve().parent


def sh(cmd, cwd=None, check=True, capture=True, env=None):
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=capture, env=env)
    if check and r.returncode != 0:
        raise SystemExit(f"command failed ({r.returncode}): {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r


def load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def validate_specs(specs, config):
    ids = [t["id"] for t in specs["tasks"]]
    for i in ids:
        uuid.UUID(i)
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate task ids")
    labels = [t["label"] for t in specs["tasks"]]
    if len(set(labels)) != len(labels):
        raise SystemExit("duplicate task labels")
    cids = [c["id"] for c in config["conditions"]]
    for i in cids:
        uuid.UUID(i)
    if len(set(cids)) != len(cids):
        raise SystemExit("duplicate condition ids")


def branch_name(task_id, cond_label):
    return f"t-{task_id}-{cond_label.lower()}"


def ensure_upstream(config):
    up = pathlib.Path(config["upstream_dir"])
    if not up.exists():
        up.parent.mkdir(parents=True, exist_ok=True)
        sh(["git", "clone", "--quiet", config["upstream_url"], str(up)])
    sh(["git", "-C", str(up), "fetch", "--quiet", "origin"], check=False)
    sh(["git", "-C", str(up), "checkout", "--quiet", "--detach", config["base_commit"]])
    head = sh(["git", "-C", str(up), "rev-parse", "HEAD"]).stdout.strip()
    if head != config["base_commit"]:
        raise SystemExit(f"upstream HEAD {head} != base {config['base_commit']}")
    return up


def build_repo(config, rebuild):
    repo = pathlib.Path(config["repo_dir"])
    up = pathlib.Path(config["upstream_dir"])
    if repo.exists():
        if not rebuild:
            print(f"repo exists at {repo}; use --rebuild to recreate")
            return repo
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    # Export the base tree without history.
    tar = subprocess.Popen(["git", "-C", str(up), "archive", config["base_commit"]], stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", str(repo)], stdin=tar.stdout, check=True)
    tar.wait()
    (repo / "CHANGES.md").unlink(missing_ok=True)
    gi = repo / ".gitignore"
    existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
    extra = [line for line in (".venv/", ".claude/", ".mypy_cache/", ".ruff_cache/", ".pytest_cache/") if line not in existing.split("\n")]
    gi.write_text(existing.rstrip("\n") + "\n" + "\n".join(extra) + "\n", encoding="utf-8")
    # venv with click editable and the check tools
    sh([sys.executable, "-m", "venv", str(repo / ".venv")])
    pip = str(repo / ".venv" / "bin" / "pip")
    sh([pip, "install", "-q", "--upgrade", "pip"], check=False)
    sh([pip, "install", "-q", "-e", str(repo), *config["venv_packages"]])
    sh(["git", "init", "-q", "-b", "base"], cwd=repo)
    sh(["git", "config", "user.email", "harness@example.invalid"], cwd=repo)
    sh(["git", "config", "user.name", "harness"], cwd=repo)
    sh(["git", "add", "-A"], cwd=repo)
    sh(["git", "commit", "-q", "-m", "base"], cwd=repo)
    print(f"built repo at {repo}")
    return repo


def reset_to(repo, ref):
    sh(["git", "checkout", "-q", "-f", ref], cwd=repo)
    sh(["git", "reset", "-q", "--hard"], cwd=repo)
    sh(["git", "clean", "-qfdx", "-e", ".venv", "-e", ".mypy_cache"], cwd=repo)


def strip_function(path, name):
    """Delete one top-level function (with its decorators) from a Python file."""
    import ast
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    node = next((n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)
    if node is None:
        raise SystemExit(f"strip_tests: {name} not found in {path}")
    start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
    end = node.end_lineno
    lines = src.splitlines(keepends=True)
    # also drop the blank lines that followed the function
    while end < len(lines) and lines[end].strip() == "":
        end += 1
    path.write_text("".join(lines[:start] + lines[end:]), encoding="utf-8")


def build_task(config, specs_task, repo, up, hidden_root):
    tid = specs_task["id"]
    reset_to(repo, "base")
    hidden_files = []
    if specs_task.get("source_commit"):
        sha = specs_task["source_commit"]
        # Three-way revert in the upstream clone (handles later edits and renames), then
        # transfer only the src/ and tests/ results into the history-free repo.
        up_s = str(up)
        sh(["git", "-C", up_s, "checkout", "-q", "-f", "--detach", config["base_commit"]])
        sh(["git", "-C", up_s, "reset", "-q", "--hard"])
        sh(["git", "-C", up_s, "clean", "-qfd"])
        r = subprocess.run(["git", "-C", up_s, "revert", "--no-commit", "--no-edit", sha], text=True, capture_output=True)
        if r.returncode != 0:
            unmerged = sh(["git", "-C", up_s, "diff", "--name-only", "--diff-filter=U"]).stdout.split()
            in_scope = [p for p in unmerged if p.startswith("src/") or p.startswith("tests/")]
            if in_scope or not unmerged:
                subprocess.run(["git", "-C", up_s, "revert", "--abort"], capture_output=True)
                sh(["git", "-C", up_s, "reset", "-q", "--hard"])
                raise SystemExit(f"{specs_task['label']}: revert of {sha} conflicts in {in_scope or 'unknown'}:\n{r.stdout}\n{r.stderr}")
            # Conflicts only outside src/ and tests/ (the changelog): keep the base version of those.
            sh(["git", "-C", up_s, "checkout", "-q", "HEAD", "--", *unmerged])
        status = sh(["git", "-C", up_s, "diff", "--cached", "--name-status"]).stdout
        subprocess.run(["git", "-C", up_s, "revert", "--quit"], capture_output=True)
        for line in status.strip().splitlines():
            parts = line.split("\t")
            code, paths = parts[0], parts[1:]
            if code.startswith("R") and len(paths) == 2:
                touched = [(paths[0], False), (paths[1], True)]
            else:
                touched = [(paths[-1], not code.startswith("D"))]
            for rel, present in touched:
                if not (rel.startswith("src/") or rel.startswith("tests/")):
                    continue
                dest = repo / rel
                if present and (up / rel).exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(up / rel, dest)
                else:
                    dest.unlink(missing_ok=True)
                if rel.startswith("tests/") and rel not in hidden_files:
                    hidden_files.append(rel)
        sh(["git", "-C", up_s, "reset", "-q", "--hard"])
        sh(["git", "-C", up_s, "clean", "-qfd"])
    # Later tests that depend on the reverted change: remove them from the base tree and
    # keep their file in the hidden set so the HEAD version is restored at check time.
    for rel, func in specs_task.get("strip_tests", []):
        strip_function(repo / rel, func)
        if rel not in hidden_files:
            hidden_files.append(rel)
    if specs_task.get("source_commit") or specs_task.get("strip_tests"):
        sh(["git", "add", "-A"], cwd=repo)
        hidden_files = sorted(hidden_files)
    hdir = hidden_root / tid
    if hdir.exists():
        shutil.rmtree(hdir)
    for rel in hidden_files:
        content = sh(["git", "-C", str(up), "show", f"{config['base_commit']}:{rel}"]).stdout
        dest = hdir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    for src_rel, dest_rel in specs_task.get("hidden_extra", []):
        dest = hdir / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / src_rel, dest)
        hidden_files.append(dest_rel)
    branches = {}
    for cond in config["conditions"]:
        claude_md = (HERE / cond["claude_md"]).read_text(encoding="utf-8")
        (repo / "CLAUDE.md").write_text(claude_md, encoding="utf-8")
        sh(["git", "add", "-A"], cwd=repo)
        bname = branch_name(tid, cond["label"])
        sh(["git", "checkout", "-q", "-B", bname], cwd=repo)
        sh(["git", "commit", "-q", "--allow-empty", "-m", f"task {specs_task['label']} condition {cond['label']}"], cwd=repo)
        branches[cond["id"]] = {"branch": bname, "commit": sh(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()}
        # Next condition starts from the same task tree: drop the commit's CLAUDE.md change only.
        sh(["git", "checkout", "-q", "-f", "--detach", "HEAD"], cwd=repo)
    return hidden_files, branches


def verify_task(config, task, repo, hidden_root):
    py = str(repo / config["venv_python"])
    cond_a = config["conditions"][0]
    reset_to(repo, task["branches"][cond_a["id"]]["branch"])
    full = subprocess.run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x"], cwd=repo, text=True, capture_output=True)
    full_tail = (full.stdout.strip().splitlines() or [""])[-1]
    hidden_tail = ""
    if task["hidden_tests"]:
        for rel in task["hidden_tests"]:
            src = hidden_root / task["id"] / rel
            dest = repo / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
        pytest_targets = [f for f in task["hidden_tests"] if f.startswith("tests/") and not f.startswith("tests/typing/")]
        typing_targets = [f for f in task["hidden_tests"] if f.startswith("tests/typing/")]
        pytest_fails = False
        mypy_fails = False
        if pytest_targets:
            h = subprocess.run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", *pytest_targets], cwd=repo, text=True, capture_output=True)
            hidden_tail = (h.stdout.strip().splitlines() or [""])[-1]
            pytest_fails = h.returncode != 0
        if typing_targets:
            m = subprocess.run([str(repo / ".venv" / "bin" / "mypy")], cwd=repo, text=True, capture_output=True)
            hidden_tail += f" | mypy rc={m.returncode}"
            mypy_fails = m.returncode != 0
        hidden_ok = pytest_fails or mypy_fails
    else:
        hidden_ok = True
    reset_to(repo, "base")
    status = "OK" if full.returncode == 0 and hidden_ok else "PROBLEM"
    print(f"  {task['label']:3} {status:7} base suite: {full_tail} | hidden: {hidden_tail or 'n/a'}")
    return status == "OK"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true", help="delete and recreate the repo and venv")
    ap.add_argument("--verify", action="store_true", help="check each task base passes and hidden tests fail")
    args = ap.parse_args()
    config = load_json(HERE / "config.json")
    specs = load_json(HERE / "task_specs.json")
    validate_specs(specs, config)
    up = ensure_upstream(config)
    repo = build_repo(config, args.rebuild)
    hidden_root = HERE / "tasks" / "hidden"
    hidden_root.mkdir(parents=True, exist_ok=True)
    footer = (HERE / "tasks" / "footer.md").read_text(encoding="utf-8").strip()
    footer_q = (HERE / "tasks" / "footer_q.md").read_text(encoding="utf-8").strip()
    tasks = []
    for st in specs["tasks"]:
        hidden_files, branches = build_task(config, st, repo, up, hidden_root)
        body = (HERE / st["prompt_file"]).read_text(encoding="utf-8").strip()
        prompt = body + "\n\n" + (footer_q if st["type"] == "find" else footer)
        tasks.append({
            "id": st["id"], "label": st["label"], "type": st["type"], "length": st["length"],
            "source_commit": st.get("source_commit"), "prompt": prompt,
            "branches": branches, "hidden_tests": hidden_files, "checks": st["checks"],
            "function_metrics": st.get("function_metrics", []), "answer_key": st.get("answer_key"),
        })
        print(f"built {st['label']}: hidden tests {hidden_files or 'none'}")
    reset_to(repo, "base")
    out = {"base_commit": config["base_commit"], "plugin_commit": (HERE / "private" / "plugin_commit.txt").read_text().strip()
           if (HERE / "private" / "plugin_commit.txt").exists() else None, "tasks": tasks}
    (HERE / "tasks.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote tasks.json with {len(tasks)} tasks")
    if args.verify:
        print("verifying task bases:")
        ok = all([verify_task(config, t, repo, hidden_root) for t in tasks])
        print("verify:", "all OK" if ok else "PROBLEMS above")


if __name__ == "__main__":
    main()
