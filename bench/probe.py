"""First-turn prompt size per plugin: one trivial prompt, hooks off except where noted."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
P = ["codex@openai-codex", "frontend-design@claude-plugins-official", "ponytail@ponytail", "caveman@caveman",
     "cc-plugin-you-should-know@builtin", "pstack@cursor-plugins", "agentic-utils-svelte-lsp@agentic-utils", "pyright-lsp@claude-plugins-official"]
def cfg(on=(), hooks=False, style="default"):
    s = {"outputStyle": style, "enabledPlugins": {p: p in on for p in P}}
    if not hooks: s["disableAllHooks"] = True
    return s
C = {"none": cfg(), "hooks_only": cfg(hooks=True), "concise_style": cfg(style="Concise"), "all_current": {}}
C.update({p.split("@")[0]: cfg(on=[p]) for p in P})
def run(name):
    p = subprocess.run(["claude", "-p", "Reply with OK.", "--output-format", "json", "--model", "sonnet", "--effort", "low",
                        "--strict-mcp-config", "--no-session-persistence", "--permission-mode", "auto", "--settings", json.dumps(C[name])],
                       cwd=os.path.join(sys.argv[1], "template"), capture_output=True, text=True, timeout=300)
    r = json.loads(p.stdout); u = r["usage"]
    return name, u["input_tokens"] + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0), r["num_turns"], r["total_cost_usd"]
with ThreadPoolExecutor(4) as ex:
    rows = list(ex.map(run, C))
base = dict((n, t) for n, t, _, _ in rows)["none"]
for n, t, turns, c in sorted(rows, key=lambda r: r[1]):
    print(f"{n:28} {t:>7} tokens  +{t-base:>6}  turns {turns}  ${c:.3f}")
