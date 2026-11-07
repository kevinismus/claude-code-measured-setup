"""Headless A/B benchmark of Claude Code config layers.

Usage: python3 -I bench.py <bench_dir> <reps> [cfg,cfg] [task,task]
"""
import json, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

BENCH = sys.argv[1]
REPS = int(sys.argv[2])
ALL_PLUGINS = ["codex@openai-codex", "frontend-design@claude-plugins-official", "ponytail@ponytail", "caveman@caveman",
               "cc-plugin-you-should-know@builtin", "pstack@cursor-plugins", "agentic-utils-svelte-lsp@agentic-utils",
               "pyright-lsp@claude-plugins-official"]
CONFIGS = {
    "A_current": ({"CAVEMAN_DEFAULT_MODE": "ultra", "PONYTAIL_DEFAULT_MODE": "ultra"}, {}),
    "B_cave_pony_full": ({"CAVEMAN_DEFAULT_MODE": "ultra", "PONYTAIL_DEFAULT_MODE": "full"}, {"outputStyle": "default"}),
    "C_concise_only": ({}, {"outputStyle": "Concise", "enabledPlugins": {"caveman@caveman": False, "ponytail@ponytail": False}}),
    "R_fixed": ({"CAVEMAN_DEFAULT_MODE": "ultra", "PONYTAIL_DEFAULT_MODE": "full"}, {"outputStyle": "default"}),
    "R_fixed_opus_high": ({"CAVEMAN_DEFAULT_MODE": "ultra", "PONYTAIL_DEFAULT_MODE": "full"}, {"outputStyle": "default"}),
    "R_fixed_opus_xhigh": ({"CAVEMAN_DEFAULT_MODE": "ultra", "PONYTAIL_DEFAULT_MODE": "full"}, {"outputStyle": "default"}),
    "D_no_addons": ({}, {"outputStyle": "default", "disableAllHooks": True, "enabledPlugins": {p: False for p in ALL_PLUGINS}}),
}
TASKS = {
    "T1_explain": ("Does low_stock in inventory.py include an item whose qty equals the threshold? Answer and explain briefly.",
                   lambda d, r: bool(re.search(r"\b(no|not|exclud)", r, re.I))),
    "T2_bugfix": ("The test suite (python3 -m unittest) fails. Find the root cause, fix it, and confirm the tests pass. Do not edit the tests.",
                  lambda d, r: tests_pass(d, "test_inventory") and same(d, "test_inventory.py")),
    "T3_feature": ("Add restock(items, sku, amount) to inventory.py: increase the qty of the item with that sku, raise KeyError for an unknown sku. Add tests for it.",
                   lambda d, r: tests_pass(d, "test_restock_hidden", hidden=True)),
    "T4_review": ("Review the proposed change in change.diff for bugs. Do not apply it.",
                  lambda d, r: bool(re.search(r"(while iterat|during iterat|mutat|skip)", r, re.I))),
    "T5_advice": ("What should a CLAUDE.md for a small Python repo like this one contain? Give your recommendation.",
                  lambda d, r: None),
}


def tests_pass(d, mod, hidden=False):
    if hidden:
        shutil.copy(os.path.join(BENCH, "hidden", mod + ".py"), d)
    return subprocess.run([sys.executable, "-m", "unittest", "-q", mod], cwd=d, capture_output=True).returncode == 0


def same(d, f):
    return open(os.path.join(d, f)).read() == open(os.path.join(BENCH, "template", f)).read()


def changed_lines(d):
    out = subprocess.run(["diff", "-r", "-x", "__pycache__", "-x", "test_restock_hidden.py", os.path.join(BENCH, "template"), d],
                         capture_output=True, text=True).stdout
    return sum(1 for l in out.splitlines() if l.startswith("> "))


def run(job):
    cfg, task, rep = job
    env_over, settings = CONFIGS[cfg]
    prompt, check = TASKS[task]
    d = os.path.join(BENCH, "runs", f"{cfg}__{task}__{rep}")
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(os.path.join(BENCH, "template"), d)
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", "--model", "opus" if "opus" in cfg else "sonnet", "--effort", "xhigh" if "xhigh" in cfg else "high",
           "--strict-mcp-config",
           "--no-session-persistence", "--permission-mode", "auto", "--max-budget-usd", "2", "--settings", json.dumps(settings)]
    t = time.time()
    p = subprocess.run(cmd, cwd=d, env={**os.environ, **env_over}, capture_output=True, text=True, timeout=900)
    init, res, tools = {}, {}, []
    for line in p.stdout.splitlines():
        try:
            m = json.loads(line)
        except ValueError:
            continue
        if m.get("type") == "system" and m.get("subtype") == "init":
            init = m
        if m.get("type") == "assistant":
            for c in m["message"].get("content", []):
                if c.get("type") == "tool_use":
                    tools.append(c["name"] + ":" + json.dumps(c["input"])[:140])
        if m.get("type") == "user":
            for c in m["message"].get("content", []) if isinstance(m["message"].get("content"), list) else []:
                if c.get("type") == "tool_result" and c.get("is_error"):
                    tools.append("ERROR:" + str(c.get("content"))[:140])
        if m.get("type") == "result":
            res = m
    text = res.get("result", "") or ""
    u = res.get("usage", {})
    row = {"cfg": cfg, "task": task, "rep": rep, "ok": check(d, text), "cost": res.get("total_cost_usd"),
           "out_tok": u.get("output_tokens"), "in_tok": u.get("input_tokens"), "cache_read": u.get("cache_read_input_tokens"),
           "cache_write": u.get("cache_creation_input_tokens"), "turns": res.get("num_turns"), "secs": round(time.time() - t, 1),
           "answer_chars": len(text), "changed_lines": changed_lines(d), "style": init.get("output_style"),
           "plugins": sorted(x.get("name", "") for x in init.get("plugins", [])), "error": res.get("is_error"),
           "rc": p.returncode, "tools": tools}
    with open(os.path.join(BENCH, "results", f"{cfg}__{task}__{rep}.json"), "w") as f:
        json.dump({**row, "answer": text, "stderr": p.stderr[-2000:]}, f, indent=1)
    print(json.dumps(row), flush=True)
    return row


cfgs = sys.argv[3].split(",") if len(sys.argv) > 3 else list(CONFIGS)
tasks = sys.argv[4].split(",") if len(sys.argv) > 4 else list(TASKS)
jobs = [(c, t, r) for r in range(REPS) for c in cfgs for t in tasks]
with ThreadPoolExecutor(4) as ex:
    list(ex.map(run, jobs))
