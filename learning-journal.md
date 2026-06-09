# Learning Journal

## 2026-06-09 — graphify graph built

- **Command:** `python -m graphify update .` (AST-only, no API key needed).
- **Result:** `graphify-out/` with 243 nodes, 539 edges, 18 communities.
- **Query example:** `python -m graphify query "How does apply work?"` — BFS over `graph.json`.
- **PATH:** Still use `python -m graphify` on Windows unless user Scripts dir is on PATH.
- **Next:** Re-run `update .` after code changes; open `graphify-out/graph.html` for viz; continue star-list `apply` workflow.

## 2026-06-09 — graphify CLI not found on Windows

- **Workaround:** `python -m graphify <command>` instead of bare `graphify`.
