---
description: >-
  Plan mode read-only boundary and tool allowlist, approval hierarchy (plan <
  default < autoEdit < yolo), tool gotchas (replace exact match, shell chaining
  validation, web_fetch localhost risk, glob sorts by mtime), headless exit
  codes, system prompt firmware vs strategy, sandbox persistence on Windows
---

# Tools and Modes

## Approval Mode Hierarchy

`plan` < `default` < `autoEdit` < `yolo`

- **Plan mode** — read-only research, auto-routes to Pro model for planning and
  Flash for implementation (if `general.plan.modelRouting` enabled)
- **Default** — manual confirmation for each mutating tool
- **AutoEdit** — auto-approve safe edit tools
- **Yolo** — auto-approve everything (CLI flag only, not in settings)

In non-interactive/headless contexts, Plan Mode transitions are auto-approved
and implementation uses Yolo mode.

Source: tool definitions in `core/src/tools/definitions/coreTools.ts`,
individual tools in `core/src/commands/`, tool registry in
`core/src/tools/tool-registry.ts`.

## Plan Mode Tool Boundary

Only allows: read-only file ops, search, MCP read-only tools, planning tools,
memory, skills, `ask_user`. Plus `write_file`/`replace` restricted to Markdown
files in the plans directory (`~/.gemini/tmp/<project>/<session>/plans/`).

**Gotcha:** Manual mode toggle (`/plan`, `Shift+Tab`) does NOT fire hooks. Only
agent-initiated `enter_plan_mode`/`exit_plan_mode` tool calls trigger hooks.

**Gotcha:** Custom plan directory must be within project root and requires
policy updates to allow write access. Custom directories are NOT auto-cleaned by
session retention (only temp dirs are).

**Gotcha:** Exiting plan mode requires choosing `DEFAULT` or `AUTO_EDIT`. User
must reach informal agreement on the plan BEFORE calling `exit_plan_mode`.

## Tool Gotchas

**`replace` requires exact match:** `old_string` must match exactly once or the
operation fails. Set `allow_multiple: true` for bulk replacements.

**Shell command chaining is strict:** Commands with `&&`, `||`, `;` are split
and each part validated separately. If ANY part fails, the entire chain is
blocked. Windows uses `powershell.exe -NoProfile -Command`, others use
`bash -c`.

**`web_fetch` can access localhost and private network addresses.** Security
risk with untrusted prompts. Always requires confirmation in Plan Mode.

**`glob` returns files sorted by modification time (newest first)**, not
alphabetical. Auto-excludes `node_modules` and `.git`.

**`grep_search` uses git grep when available**, falls back to system grep or
JS-based search. Performance varies.

**`ask_user` limits:** Max 4 questions per call, choice questions need 2-4
options, header max 16 chars, option labels 1-5 words. Returns JSON indexed by
string position (`{"answers": {"0": "...", "1": "..."}}`).

**All file ops confined to `rootDirectory`.** Absolute paths required in tool
calls. `read_file` supports images, audio, and PDFs.

## Headless Mode

Exit code semantics beyond 0/1:

- `42` — input error
- `53` — turn limit exceeded

Two output formats: standard JSON (single object) or streaming JSONL. Final
result includes per-model token breakdowns. TTY detection or `-p`/`--prompt`
flag triggers headless.

## Session Management

- Sessions are **project-specific** — switching directories switches history
- Named checkpoints via `/resume save <name>` and `/resume resume <name>`
- Session retention: default 30 days, configurable with `maxAge`, `maxCount`,
  `minRetention`
- `maxSessionTurns` limit: interactive stops requesting, non-interactive exits
  with error
- Worktrees (experimental): stored in `.gemini/worktrees/`, no auto-cleanup,
  manual `npm install` per worktree, uncommitted changes preserved

## System Prompt Override

`GEMINI_SYSTEM_MD` completely **replaces** the built-in system prompt
(firmware). This is a firmware/strategy distinction:

- **system.md (firmware):** Safety, tool protocols, approval mechanics
- **GEMINI.md (strategy):** Persona, goals, project context

Export default first with `GEMINI_WRITE_SYSTEM_MD=1`. Variable substitution:
`${AgentSkills}`, `${SubAgents}`, `${AvailableTools}`, `${write_file_ToolName}`.
UI shows `|⌐■_■|` when active.

## Sandbox Gotchas

- **Windows:** Integrity level changes **persist on files** after sandbox ends.
  Manual reset: `icacls "path" /setintegritylevel Medium`
- **macOS seatbelt:** Default `permissive-open` profile
- **gVisor/runsc:** Strongest isolation, explicit via `GEMINI_SANDBOX=runsc`
- **LXC/LXD:** Requires pre-created running container, can't auto-create

See also:

- [hooks.md](hooks.md) — plan mode toggle doesn't fire hooks (only
  agent-initiated tool calls do), BeforeTool/AfterTool events for tool-level
  interception
- [configuration-and-policies.md](configuration-and-policies.md) — approval
  cascading rules, YOLO CLI-flag-only restriction, deny-removes-from-context
  behavior
- [architecture.md](architecture.md) — tool registry entry point, model fallback
  chain affecting plan mode routing
