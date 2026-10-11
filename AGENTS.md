# Project Rules & Guidelines

## RTK / GTK Command Guidelines
- **Proxy**: All standard bash/terminal commands are optimized and filtered via RTK (`rtk`). If `gtk` is invoked, treat as alias/synonym for `rtk`.
- **Git Operations**: Run `rtk git status`, `rtk git diff`, `rtk git log`, `rtk git commit`, `rtk git push`.
- **File & Directory Inspection**: Use `rtk ls`, `rtk tree`, `rtk find`, or `rtk read` for token-optimized listings.
- **Searching**: Prefer ripgrep (`rtk rg` / `rg`) wherever possible over standard grep or raw file dumps to minimize token usage.
- **Diagnostics & Testing**: Run `rtk test` or `rtk err` to isolate failures without context bloat.

## Git & Workflow Guidelines
- **No Unrequested Issues**: Never create GitHub issues automatically or proactively for each feature. Only create GitHub issues when explicitly requested by the user.
- **No Unrequested Branches**: Do not create separate Git branches for features or changes unless the user explicitly asks for a branch. Work and commit directly on the active branch.

## Context-Mode Routing Guidelines
- **Derive, Do Not Dump**: Do not dump entire files into context. Print only needed matches, counts, or slices.
- **Tool Routing**:
  - For data analysis, transformations, or counts: execute inside the sandbox via `context-mode/ctx_execute` and print derived results.
  - For examining large files (>200 lines): use `context-mode/ctx_execute_file`.
  - For multi-command exploration: use `context-mode/ctx_batch_execute`.
  - For external web pages: use `context-mode/ctx_fetch_and_index` then query via `context-mode/ctx_search`.

## Ponytail (Lazy Senior Dev Mode) Guidelines
- **Stop at the first rung that holds**:
  1. Does this need to be built at all? (YAGNI)
  2. Does it already exist in this codebase? Reuse existing helpers/utils/patterns.
  3. Does the standard library already do this?
  4. Does a native platform feature cover it?
  5. Does an already-installed dependency solve it?
  6. Can this be one line?
  7. Only then: write the minimum code that works.
- **Bug fix = root cause, not symptom**: Fix the shared function/path once rather than patching multiple callers.
- **Rules**:
  - No unrequested abstractions, boilerplate, or avoidable dependencies.
  - Deletion over addition. Boring over clever. Fewest files possible.
  - Shortest working diff wins once the problem is understood.
  - Mark deliberate shortcuts with a `ponytail:` comment naming ceiling and upgrade path.
  - Non-trivial logic leaves ONE runnable check (assert-based self-check, no frameworks). Trivial one-liners need no test.

## Caveman Guidelines
Respond terse like smart caveman. All technical substance stay. Only fluff die.

- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging.
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: `[thing] [action] [reason]. [next step].`
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"
- Auto-Clarity: normal prose for security warnings, irreversible actions, user confused. Resume caveman after.

## CodeGraph
In repositories indexed by CodeGraph (a `.codegraph/` directory exists at repo root):
- MCP tool: `codegraph_explore` answers source, call paths, and blast radius in one call.
- Shell: `codegraph explore "<symbol names or question>"` prints AST and symbol graphs.
- Use CodeGraph BEFORE grep/find or raw file reads when exploring codebase architecture or tracing callers.

## Serena Semantic Code Tools
Serena MCP provides Language Server Protocol (LSP) backed semantic coding tools, token-efficient AST symbol search, reference-aware refactoring, and persistent project memories.
- **Project Activation**: Workspace registered as `prog-metal-structures`. Active project path is the repository root.
- **Symbol Inspection Over File Dumps**: Use `get_symbols_overview` for file symbol trees, `find_symbol` for specific function/class definitions.
- **Pattern & Reference Search**: Use `search_for_pattern` to locate symbols and `find_referencing_symbols` to analyze blast radius.
- **Atomic Refactoring**: Use `rename_symbol`, `safe_delete_symbol`, and `replace_symbol_body` for AST-safe edits.
- **Persistent Memory**: Consult and update `read_memory`, `write_memory`, and `list_memories`. Current core memories: `mem:core`, `mem:tech_stack`, `mem:suggested_commands`, `mem:conventions`, `mem:task_completion`.
- **Diagnostics**: Use `get_diagnostics_for_file` to inspect language server diagnostics.

## Project Specific Invariants
- **Python Indentation**: Strictly 2-space indentation on all Python code (`scripts/*.py`). Never use 4 spaces.
- **JSON Schemas**: All processed datasets must validate against schemas in `schemas/`.

## Testing & TDD Guidelines
- **Test-Driven Development (TDD)**: Follow the TDD workflow: write failing tests first to define expectations or reproduce bugs, implement minimal code to make them pass, and verify test passes before completing work.
- **Test Directory**: Store all test suites in the `tests/` directory (e.g. `tests/test_*.py`). Execute tests via `uv run pytest`.

## Python & Package Management Guidelines
- **Runner**: Always use `uv` to execute Python scripts (e.g. `uv run python scripts/<script>.py`).
- **Dependencies**: Keep `pyproject.toml` and `uv.lock` synchronized using `uv add` / `uv remove` when adding or updating dependencies.

## Task Automation (Taskfile.yml) Guidelines
- **Sync New Functionality**: Keep `Taskfile.yml` up to date. Whenever adding new scripts, workflows, or CLI capabilities to the repo, add corresponding task definitions to `Taskfile.yml` with clear descriptions and parameter forwarding (`{{.CLI_ARGS}}`).

## MIDI Search Guidelines
- **Local Dataset First**: When searching for MIDI files, always search the local repository `/home/nicholas/git/asigalov61/Tegridy-MIDI-Dataset` first before searching online.
- **Preferred Search Engines & Archives**: When searching online for MIDI files, prioritize search engines and archives such as FreeMidi.org, BitMidi.com, and Metal-MIDI Archives (`metal-midi.grahamdowney.com`).
- **Google Dorking ("Index Of")**: When web searching for MIDI files, use the "Index Of" dork format (e.g. `intitle:"index of" "<artist/band>" ".mid" OR ".midi"`).
- **Online MIDI Sources**: When searching for online MIDI sources or external sites to search, consult the curated list in `/home/nicholas/git/albertmeronyo/awesome-midi-sources/README.md`.
