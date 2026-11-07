# Claude Code, measured

A small, generic Claude Code setup, and the benchmark that shaped it.

I ran Claude Code with several "token-saving" add-ons stacked together and assumed they were saving usage. When I measured, answers were 37% shorter but each task cost 31% more than running without them. This repository has the setup I kept, the harness I used and the raw results, so you can check the numbers or run them against your own configuration.

## Results

Five fixed tasks on a small Python repo (answer a code question, fix a failing test, add a feature with tests, review a diff, give written advice), run headless with `claude -p --output-format json`. Auto permission mode, two runs per task on Sonnet at high effort; one run per task for the Opus rows.

| Configuration | Cost per task | Answer length | Output tokens | Turns |
|---|---|---|---|---|
| No plugins or hooks | $0.083 | 1,085 chars | 947 | 3.0 |
| Full stack (terse output style, caveman ultra, ponytail ultra, hooks) | $0.109 | 688 chars | 923 | 3.9 |
| Cleaned-up stack (caveman ultra, ponytail full, hooks) | $0.103 | 675 chars | 796 | 3.2 |
| Cleaned-up stack on Opus, high effort | $0.229 | 910 chars | 1,097 | 3.6 |
| Cleaned-up stack on Opus, xhigh effort | $0.238 | 958 chars | 1,475 | 4.0 |

Every configuration passed every graded task. Costs are the API-equivalent `total_cost_usd` that Claude Code reports.

What the numbers say:

- **Output is a small share of the work.** About 1,000 output tokens per task, against 110,000 to 135,000 tokens of context read or cached. Terse modes shorten what you read; they barely change what you use.
- **Fixed context adds up.** With no plugins (Claude Code's own prompt and tools, my CLAUDE.md and the skills list), a one-line prompt sent about 38,400 tokens. The add-ons together added about 5,300 (caveman about 1,900, ponytail about 650, the terse output style about 500, the rest under 350 each). That prefix rides along on every turn.
- **Tools can misfire together.** A first run, with only `Bash(python3:*)` allowed, showed +44% cost and nearly twice the turns. [RTK](https://github.com/rtk-ai/rtk) rewrites `ls` to `rtk ls`, the rewritten commands matched no allow rule, so each was denied and retried. Auto mode removed the denials. Those first-round results are kept in `bench/results/round1-acceptedits` for reference.
- **Higher effort mostly bought time.** Opus at xhigh cost about 4% more than at high, with 34% more output tokens and slower runs, for the same results here.

Limits: a toy repo, small samples and simple tasks. This says nothing about quality on hard problems, and long sessions may behave differently because cached context gets cheaper to reuse. Run it on your own setup before drawing conclusions.

## What's here

| Path | What it is |
|---|---|
| `SETUP-PROMPT.md` | One prompt to paste into Claude Code. It inspects your config, proposes changes and waits for approval. |
| `examples/CLAUDE.md` | A global CLAUDE.md that maintains itself under explicit rules. |
| `examples/settings.json` | Auto permission mode, deny rules for secrets and destructive commands, and the guard hook. |
| `hooks/block-dangerous-commands.js` | PreToolUse hook that denies catastrophic shell commands. It does not log the blocked command text. |
| `hooks/test-block-dangerous-commands.js` | Regression test: commands the guard must block and must allow. |
| `agents/explorer.md` | A read-only search subagent on Haiku that returns `file:line` references instead of file contents. |
| `bench/` | The benchmark harness, task repo, hidden test and raw results. |

## Quick start

Paste the prompt in `SETUP-PROMPT.md` into Claude Code, or copy the pieces by hand:

```sh
mkdir -p ~/.claude/hooks ~/.claude/agents
cp hooks/*.js ~/.claude/hooks/
cp agents/explorer.md ~/.claude/agents/
node ~/.claude/hooks/test-block-dangerous-commands.js
```

Then merge `examples/settings.json` and `examples/CLAUDE.md` into your own files rather than overwriting them.

Two habits worth adding outside Claude Code:

- **Send `rm` to the trash.** `alias rm="trash"` in your shell profile (built in on macOS 15 and later; on Linux, install `trash-cli` and alias to `trash-put`). It's a recovery layer, not a guarantee: absolute paths, scripts and other tools can still delete files.
- **If you use RTK without auto mode**, allow its read-only subcommands (`rtk ls`, `rtk read`, `rtk grep`, `rtk find`, `rtk git status`, `rtk git diff`, `rtk git log`), or rewritten commands will be denied and retried.

## Run the benchmark

Requires Python 3 and a logged-in `claude` CLI. Each run is billed to your account or counted against your plan.

```sh
cd bench
python3 bench.py "$PWD" 2                    # all configurations, 2 runs each
python3 bench.py "$PWD" 1 R_fixed T2_bugfix  # one configuration, one task
python3 summary.py results                   # summarise new runs
python3 summary.py results/round2-auto       # summarise the published runs
python3 probe.py "$PWD"                      # fixed context per plugin
```

The configurations in `bench.py` and `probe.py` match the plugins I use. Edit `CONFIGS` and the plugin list to compare your own.

## License

MIT
