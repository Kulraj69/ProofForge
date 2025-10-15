# ProofForge — FastAPI prototype (Swagger UI)

Evaluate GitHub repos and anchor explainable evaluation on Hedera testnet.

## What this does (prototype)
- Accepts a GitHub repo URL via REST (Swagger UI).
- Runs a simple explainable evaluator that returns `{score, trace}`.
- Submits a proof (score + trace hash) to a Hedera Consensus Topic (testnet).
- Returns result & Hedera transaction id.

## Quickstart (local)

### Prereqs
- Python 3.10+
- GitHub token (recommended) - optional but avoids rate limits
- Hedera testnet account (get operator id & private key) — see Hedera docs

### Install
```bash
git clone <repo-url>
cd proofforge
python -m venv .venv
source .venv/bin/activate   # mac/linux
pip install -r requirements.txt
# (or) pip install fastapi uvicorn requests hiero-sdk-python python-dotenv
```

### Run
```bash
uvicorn main:app --reload
```

Open http://localhost:8000/docs to access Swagger UI.

## API Endpoints

### POST /evaluate
Evaluates a GitHub repository and submits proof to Hedera.

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo"
}
```

**Response:**
```json
{
  "repo": "owner/repo",
  "score": 45,
  "trace": ["has tests: +20", "stars > 100: +15", "active commits: +10"],
  "trace_hash": "abc123...",
  "hedera_tx_id": "0.0.123456@1640995200.123456789",
  "timestamp": "2023-12-01T12:00:00Z"
}
```

## Architecture

- **Frontend**: Swagger UI for API testing
- **Backend**: FastAPI application
- **Evaluator**: Local rule engine (future: ASI agent)
- **Blockchain**: Hedera Consensus Service (testnet)
- **Storage**: Local JSON persistence

## License

Apache-2.0 License