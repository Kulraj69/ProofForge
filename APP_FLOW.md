# APP_FLOW.md (App flow document — step-by-step sequence)

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
```

- Submit to Hedera Consensus Topic
- Receive transaction ID

### 6 — Persist and return result
- Save to local storage (JSON file or DB)
- Return complete response:
```json
{
  "repo": "owner/repo",
  "score": 45,
  "trace": ["has tests: +20", "stars > 100: +15"],
  "trace_hash": "abc123...",
  "hedera_tx_id": "0.0.123456@1640995200.123456789",
  "timestamp": "2023-12-01T12:00:00Z"
}
```

## Error Handling

### GitHub API Errors
- Rate limiting → retry with exponential backoff
- Repository not found → return 404 with clear message
- Private repository → return 403 (requires authentication)

### Hedera Errors
- Network issues → retry submission
- Invalid credentials → return 500 with setup instructions
- Topic creation fails → fallback to local storage only

### Validation Errors
- Invalid URL format → return 400 with example
- Missing required fields → return 400 with field list

## Future Enhancements

### Phase 2: ASI Agent Integration
- Replace local evaluator with ASI agent
- More sophisticated code analysis
- Multi-language support

### Phase 3: Advanced Features
- Batch repository evaluation
- Historical trend analysis
- Custom evaluation criteria
- Webhook notifications

### Phase 4: Production Ready
- Database integration (PostgreSQL)
- Authentication and authorization
- Rate limiting and quotas
- Monitoring and logging
- Docker containerization
