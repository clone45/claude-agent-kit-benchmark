#!/usr/bin/env python3
"""Build the phase-two repo (voxglitch) with one base branch per task and condition, plus chain bases.

usage: make_tasks2.py [--rebuild] [--verify]
Reads config2.json and task_specs2.json; writes tasks2.json and tasks2/hidden/<task-uuid>/...
Branches: t-<task-uuid>-a / -b (fresh runs) and chain-a / chain-b (chained sessions; seeded bugs applied).
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


def sh(cmd, cwd=None, check=True, input_text=None):
    r = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, input=input_text)
    if check and r.returncode != 0:
        raise SystemExit(f"command failed ({r.returncode}): {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r


def load_json(p):
    return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))


def reset_to(repo, ref, keep):
    sh(["git", "checkout", "-q", "-f", ref], cwd=repo)
    sh(["git", "reset", "-q", "--hard"], cwd=repo)
    args = []
    for k in keep:
        args += ["-e", k]
    sh(["git", "clean", "-qfdx", *args], cwd=repo)


SEEDS = {
    # Euclid: a reset no longer arms the clock-ignore window, so a clock inside the window advances.
    "seed_euclid_window": ("src/modules/Euclid/EuclidEngine.hpp",
                           "            position = 0;\n            window.arm(window_samples);\n            out.struck = pattern.hit[0];",
                           "            position = 0;\n            out.struck = pattern.hit[0];"),
}


def apply_seed(repo, name):
    rel, old, new = SEEDS[name]
    p = repo / rel
    src = p.read_text(encoding="utf-8")
    if src.count(old) != 1:
        raise SystemExit(f"seed {name}: anchor text not found exactly once in {rel}")
    p.write_text(src.replace(old, new), encoding="utf-8")


def build_repo(config, rebuild):
    repo = pathlib.Path(config["repo_dir"])
    up = pathlib.Path(config["upstream_dir"])
    if not up.exists():
        sh(["git", "clone", "--quiet", config["upstream_url"], str(up)])
    sh(["git", "-C", str(up), "checkout", "-q", "--detach", config["base_commit"]])
    full = sh(["git", "-C", str(up), "rev-parse", "HEAD"]).stdout.strip()
    if repo.exists():
        if not rebuild:
            print(f"repo exists at {repo}; use --rebuild to recreate")
            return repo, full
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    tar = subprocess.Popen(["git", "-C", str(up), "archive", full], stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", str(repo)], stdin=tar.stdout, check=True)
    tar.wait()
    # Remove the project's own skills (release tooling) and add the check script.
    shutil.rmtree(repo / ".claude", ignore_errors=True)
    for src in (HERE / "tasks2" / "repo_files").rglob("*"):
        if src.is_file():
            dest = repo / src.relative_to(HERE / "tasks2" / "repo_files")
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
            dest.chmod(0o755)
    gi = repo / ".gitignore"
    existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
    extra = [line for line in (".claude/", "tests/**/*_test", "tests/**/*.o") if line not in existing.split("\n")]
    gi.write_text(existing.rstrip("\n") + "\n" + "\n".join(extra) + "\n", encoding="utf-8")
    sh(["git", "init", "-q", "-b", "base"], cwd=repo)
    sh(["git", "config", "user.email", "harness@example.invalid"], cwd=repo)
    sh(["git", "config", "user.name", "harness"], cwd=repo)
    sh(["git", "add", "-A"], cwd=repo)
    sh(["git", "commit", "-q", "-m", "base"], cwd=repo)
    print(f"built repo at {repo} from {full[:7]}")
    return repo, full


def commit_conditions(config, repo, prefix, message):
    """From the current working tree (already modified), create one branch per condition with its CLAUDE.md."""
    out = {}
    start = sh(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()
    for cond in config["conditions"]:
        sh(["git", "checkout", "-q", "-f", "--detach", start], cwd=repo)  # same starting tree each time
        # re-apply the working-tree modifications stashed as a patch
        (repo / "CLAUDE.md").write_text((HERE / cond["claude_md"]).read_text(encoding="utf-8"), encoding="utf-8")
        sh(["git", "add", "-A"], cwd=repo)
        bname = f"{prefix}-{cond['label'].lower()}"
        sh(["git", "checkout", "-q", "-B", bname], cwd=repo)
        sh(["git", "commit", "-q", "--allow-empty", "-m", f"{message} condition {cond['label']}"], cwd=repo)
        out[cond["id"]] = {"branch": bname, "commit": sh(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()}
    return out


def build_tree_commit(config, repo, seeds, hidden_dir_for, label):
    """Create a detached commit of base + seeds (no CLAUDE.md yet) and return its hash."""
    reset_to(repo, "base", config["clean_keep"])
    sh(["git", "checkout", "-q", "--detach"], cwd=repo)  # never move the base branch itself
    for s in seeds:
        apply_seed(repo, s)
    sh(["git", "add", "-A"], cwd=repo)
    sh(["git", "commit", "-q", "--allow-empty", "-m", f"tree for {label}"], cwd=repo)
    return sh(["git", "rev-parse", "HEAD"], cwd=repo).stdout.strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    config = load_json(HERE / "config2.json")
    specs = load_json(HERE / config["task_specs_file"])
    ids = [t["id"] for t in specs["tasks"]]
    for i in ids:
        uuid.UUID(i)
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate task ids")
    repo, full = build_repo(config, args.rebuild)
    hidden_root = HERE / config["hidden_root"]
    hidden_root.mkdir(parents=True, exist_ok=True)
    footer = (HERE / config["footer_file"]).read_text(encoding="utf-8").strip()
    footer_q = (HERE / config["footer_q_file"]).read_text(encoding="utf-8").strip()
    tasks = []
    for st in specs["tasks"]:
        tid = st["id"]
        hdir = hidden_root / tid
        if hdir.exists():
            shutil.rmtree(hdir)
        hidden_files = []
        if st.get("hidden") == "base_euclid_tests":
            for rel in ("tests/euclid/pattern_test.cpp", "tests/euclid/engine_test.cpp", "tests/euclid/seq3_parity_test.cpp", "tests/euclid/check.hpp"):
                dest = hdir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(sh(["git", "-C", str(pathlib.Path(config["upstream_dir"]))
                                    , "show", f"{full}:{rel}"]).stdout, encoding="utf-8")
                hidden_files.append(rel)
        elif isinstance(st.get("hidden"), list):
            for src_rel, dest_rel in st["hidden"]:
                dest = hdir / dest_rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE / src_rel, dest)
                hidden_files.append(dest_rel)
        seeds = [st["seed"]] if st.get("seed") else []
        build_tree_commit(config, repo, seeds, hdir, st["label"])
        branches = commit_conditions(config, repo, f"t-{tid}", f"task {st['label']}")
        body = (HERE / st["prompt_file"]).read_text(encoding="utf-8").strip()
        prompt = body + "\n\n" + (footer_q if st["type"] == "find" else footer)
        tasks.append({"id": tid, "label": st["label"], "type": st["type"], "length": st["length"], "seed": st.get("seed"),
                      "prompt": prompt, "prompt_body": body, "branches": branches, "hidden_tests": hidden_files,
                      "checks": st["checks"], "function_metrics": st.get("function_metrics", []), "answer_key": st.get("answer_key")})
        print(f"built {st['label']}: hidden {hidden_files or 'none'}")
    # Chain bases: every seed applied, one branch per condition.
    all_seeds = sorted({t["seed"] for t in specs["tasks"] if t.get("seed")})
    build_tree_commit(config, repo, all_seeds, None, "chain")
    chain_branches = commit_conditions(config, repo, "chain", "chain base")
    reset_to(repo, "base", config["clean_keep"])
    out = {"base_commit": full, "plugin_commit": (HERE / "private" / "plugin_commit.txt").read_text().strip(),
           "chain_order": specs["chain_order"], "chain_branches": chain_branches, "tasks": tasks}
    (HERE / config["tasks_file"]).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"wrote {config['tasks_file']} with {len(tasks)} tasks; chain order {specs['chain_order']}")
    if args.verify:
        print("verifying:")
        cond_a = config["conditions"][0]["id"]
        for t in tasks:
            reset_to(repo, t["branches"][cond_a]["branch"], config["clean_keep"])
            base_tests = subprocess.run(["bash", "scripts/vg_check.sh", "tests"], cwd=repo, text=True, capture_output=True)
            base_ok = base_tests.returncode == 0
            hidden_status = "n/a"
            if t["hidden_tests"]:
                for rel in t["hidden_tests"]:
                    dest = repo / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(hidden_root / t["id"] / rel, dest)
                hcmd = next((c["cmd"] for c in t["checks"] if c["name"] == "hidden"), None)
                h = subprocess.run(["bash", "-c", hcmd], cwd=repo, text=True, capture_output=True)
                hidden_status = "fails on base (good)" if h.returncode != 0 else "PASSES ON BASE (bad)"
            expected_base = (not base_ok) if t.get("seed") else base_ok
            print(f"  {t['label']:3} base tests {'pass' if base_ok else 'FAIL'}{' (expected: seeded)' if t.get('seed') else ''} | hidden: {hidden_status} | {'OK' if expected_base and hidden_status != 'PASSES ON BASE (bad)' else 'PROBLEM'}")
        reset_to(repo, "base", config["clean_keep"])


if __name__ == "__main__":
    main()
