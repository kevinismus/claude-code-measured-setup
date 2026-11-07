# Setup prompt

Paste the block below into Claude Code. It inspects your current configuration, proposes changes and waits for your approval before writing anything.

```text
Set up a lean, safe Claude Code configuration for me. Work in this order and stop for my approval before any write.

1. Inspect: read ~/.claude/settings.json, ~/.claude/CLAUDE.md, ~/.claude/agents/ and ~/.claude/hooks/ if they exist. Summarise what is there. Never print secret values.
2. Back up: if ~/.claude is not a git repository, propose `git init` there with a .gitignore that tracks only CLAUDE.md, settings.json, agents/, hooks/, rules/ and skills/, then commit a baseline. Never add a remote.
3. CLAUDE.md: if missing or bloated, propose a short one with a "Keeping this file current" section: add a line only when I correct you, state a lasting preference, or you hit a non-obvious fact that would cause a mistake in another project; check for an existing line first and edit it instead; delete stale lines; one instruction per bullet under a header; keep project knowledge in that project's CLAUDE.md. Keep everything I already have that passes the test "would removing this cause a mistake?".
4. Permissions in settings.json: set "permissions.defaultMode" to "auto" if this Claude Code version supports it, otherwise "default". Never set bypassPermissions. Add deny rules for reading secrets (**/.env, **/.env.*, **/*.pem, **/*.key, ~/.ssh/**, ~/.aws/**) and for destructive commands (rm -rf, git push --force, git reset --hard, sudo, curl or wget piped to a shell). Merge with existing rules; never remove mine.
5. Guard hook: write ~/.claude/hooks/block-dangerous-commands.js, a PreToolUse hook for Bash that denies catastrophic commands (rm targeting ~, $HOME, /, system directories or the current directory, including inside quotes such as bash -c "rm -rf ."; dd or mkfs to disks; fork bombs; curl or wget piped to sh; force-push to main or master; git reset --hard; git clean -f; reading .env). Export the check function. It must not log the blocked command text. Register it in settings.json.
6. Guard test: write ~/.claude/hooks/test-block-dangerous-commands.js that imports the check function and asserts a must-block list and a must-allow list (for example rm -rf node_modules, git push origin main, cat .env.example, docker build .). Run it with node and show me the result. Never test the guard by putting dangerous strings in a Bash command.
7. Safer deletes: tell me how to alias rm to trash in my shell profile (macOS 15+: built-in trash; Linux: trash-cli's trash-put). Do not edit my shell profile yourself.
8. Read-only explorer: create ~/.claude/agents/explorer.md, a subagent for broad codebase searches on the haiku model, with only read-only tools, that returns conclusions with file:line references instead of file contents. If you include Bash, say that it is no longer strictly read-only.
9. Optional, ask first: RTK command-output compression (https://github.com/rtk-ai/rtk) with `rtk init -g --hook-only`. If permissions.defaultMode is not auto, also add allow rules for its read-only subcommands (rtk ls, rtk read, rtk grep, rtk find, rtk git status, rtk git diff, rtk git log), otherwise rewritten commands get denied and retried.
10. Do not install output-style or "terse" plugins by default. If I want one, measure it first (step 11).
11. Measure: create a throwaway repo with one failing test and run three tasks (explain a function, fix the bug, review a diff) with `claude -p "<task>" --output-format json --no-session-persistence`, before and after, two runs each. Report total_cost_usd, num_turns and output tokens per configuration in a table, and say plainly if the new setup costs more.
12. Commit the final config in ~/.claude and list every file you changed and how to roll back.
```
