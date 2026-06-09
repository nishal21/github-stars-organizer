# Graph Report - github-stars-organizer  (2026-06-09)

## Corpus Check
- 31 files · ~7,949 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 243 nodes · 539 edges · 18 communities (17 shown, 1 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8d5159ba`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]

## God Nodes (most connected - your core abstractions)
1. `StarredRepo` - 28 edges
2. `StarList` - 19 edges
3. `GitHubWebClient` - 17 edges
4. `GitHubConfig` - 13 edges
5. `StarList` - 13 edges
6. `fetch_star_lists()` - 13 edges
7. `GitHub Stars Organizer` - 13 edges
8. `_cmd_plan()` - 12 edges
9. `load_config()` - 12 edges
10. `Assignment` - 12 edges

## Surprising Connections (you probably didn't know these)
- `StarredRepo` --uses--> `StarredRepo`  [INFERRED]
  tests/test_categorize.py → src/stars_organizer/models.py
- `StarredRepo` --uses--> `StarredRepo`  [INFERRED]
  tests/test_plan_format.py → src/stars_organizer/models.py
- `test_build_and_load_plan_round_trip()` --calls--> `save_plan()`  [EXTRACTED]
  tests/test_plan_format.py → src/stars_organizer/categorize.py
- `test_plan_json_structure()` --calls--> `load_plan()`  [EXTRACTED]
  tests/test_plan_format.py → src/stars_organizer/categorize.py
- `test_load_llm_config_mistral()` --calls--> `load_llm_config()`  [EXTRACTED]
  tests/test_llm_config.py → src/stars_organizer/config.py

## Import Cycles
- None detected.

## Communities (18 total, 1 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.16
Nodes (29): AsyncClient, BeautifulSoup, GitHubConfig, StarList, StarredRepo, assign_repo_to_lists(), _build_cookies(), create_star_list() (+21 more)

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (24): Path, StarredRepo, build_plan(), categorize_repo(), load_categories(), load_plan(), merge_categories(), Heuristic categorization of starred repositories into broad lists. (+16 more)

### Community 2 - "Community 2"
Cohesion: 0.14
Nodes (24): Path, _cmd_providers(), _cmd_status(), Config, config_status(), load_config(), load_llm_config(), get_provider() (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.21
Nodes (22): Assignment, CategorizationResult, LLMConfig, Response, Semaphore, Path, StarList, StarredRepo (+14 more)

### Community 4 - "Community 4"
Cohesion: 0.19
Nodes (18): Namespace, GitHubConfig, StarredRepo, save_plan(), _cmd_apply(), _cmd_consolidate(), _cmd_init(), _cmd_lists() (+10 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (16): 1. Build a plan (no credentials needed), 2. Configure credentials, 3. Preview and apply, Attribution, CLI reference, Default categories, Development, Getting your browser cookie (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.17
Nodes (11): [0.1.0] - 2026-06-08, [0.2.0] - 2026-06-08, [0.2.1] - 2026-06-08, [0.2.2] - 2026-06-08, Added, Added, Added, Changelog (+3 more)

### Community 7 - "Community 7"
Cohesion: 0.26
Nodes (10): consolidate_assignments(), consolidate_plan(), map_list_to_broad(), Merge granular AI list names down to GitHub's 32-list limit., Return a new plan dict with merged list assignments., Remap repo assignments so unique list count is <= max_lists., _score_list_name(), test_consolidate_plan_structure() (+2 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (10): assignments, cli/cli, openai/openai-python, vercel/next.js, lists, AI & LLM, Dev Tools & CLI, Web Dev & Frontend (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.18
Nodes (10): assignments, cli/cli, openai/openai-python, vercel/next.js, lists, AI & LLM, Dev Tools & CLI, Web Dev & Frontend (+2 more)

### Community 10 - "Community 10"
Cohesion: 0.29
Nodes (6): Adding category rules, Contributing, Development setup, Pull requests, Reporting issues, Run tests

### Community 11 - "Community 11"
Cohesion: 0.38
Nodes (3): Path, ApplyState, Checkpoint state for resumable apply operations.

### Community 12 - "Community 12"
Cohesion: 0.33
Nodes (5): Dogfood (organize your stars), GitHub repository, Publishing guide, PyPI release, Trusted Publishing (optional, no API token)

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): Credential handling, Reporting a vulnerability, Security Policy, Supported versions, What this tool sends externally

### Community 14 - "Community 14"
Cohesion: 0.50
Nodes (3): Attribution, github_web.py, Related projects

## Knowledge Gaps
- **50 isolated node(s):** `username`, `total`, `AI & LLM`, `Web Dev & Frontend`, `Dev Tools & CLI` (+45 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StarredRepo` connect `Community 3` to `Community 0`, `Community 1`, `Community 4`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `GitHubWebClient` connect `Community 0` to `Community 3`, `Community 4`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `ApplyState` connect `Community 11` to `Community 3`, `Community 4`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `StarredRepo` (e.g. with `Assignment` and `AsyncClient`) actually correct?**
  _`StarredRepo` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `StarList` (e.g. with `Assignment` and `AsyncClient`) actually correct?**
  _`StarList` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `GitHubWebClient` (e.g. with `Namespace` and `Path`) actually correct?**
  _`GitHubWebClient` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `GitHubConfig` (e.g. with `AsyncClient` and `BeautifulSoup`) actually correct?**
  _`GitHubConfig` has 9 INFERRED edges - model-reasoned connections that need verification._