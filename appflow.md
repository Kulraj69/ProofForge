
---

# 3) APP_FLOW.md (App flow document — step-by-step sequence)

## Actors
- **User**: posts repo link via Swagger UI (or frontend).
- **Backend**: FastAPI — orchestrator.
- **Evaluator (local)**: rule engine (or ASI agent in future).
- **Hedera**: Consensus Service (topic) to store proofs.
- **Storage**: local JSON (or DB) to persist results.

## End-to-End Flow (prototype)

### 1 — User posts repo
- Action: `POST /evaluate` with `{"repo_url":"https://github.com/owner/repo"}`
- FastAPI:
  - validates input
  - extracts `owner` and `repo` (parse URL)

### 2 — Backend fetches GitHub data
- Calls:
  - `GET https://api.github.com/repos/{owner}/{repo}` → metadata (stars, issues)
  - `GET https://api.github.com/repos/{owner}/{repo}/commits` → commits list
  - `GET https://api.github.com/repos/{owner}/{repo}/contents` → search for `test` folder
- Builds `summary = { stars, open_issues, has_tests, commit_count }`

### 3 — Evaluator runs
- Calls `evaluate_repo_summary(summary)`
  - Local prototype returns `{score: int, trace: [str]}`.
  - Each trace item is human-readable e.g. `"has tests: +20"`

### 4 — Produce immutable trace hash
- `trace_str = json.dumps(trace, sort_keys=True)`
- `trace_hash = sha256(trace_str)`

### 5 — Submit proof to Hedera
- Compose message:
```json
{
  "repo": "owner/repo",
  "score": 45,
  "trace_hash": "abc123",
  "timestamp": "ISO8601"
}
