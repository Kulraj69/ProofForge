# 🧠 ProofForge — Implementation Guide

## Overview

ProofForge evaluates GitHub repositories or pull requests through autonomous reasoning agents (using ASI) and writes verifiable proofs of their reasoning to Hedera.

## Core Components

```
/backend
 ├── main.py             # FastAPI app, all endpoints, Swagger enabled
 ├── evaluator.py        # EvaluatorAgent logic (local or ASI)
 ├── hedera_client.py    # Hedera SDK helper (Consensus Service)
 ├── github_client.py    # Fetch repo / PR metadata
 ├── models.py           # Pydantic data models
 ├── storage.json        # Local result persistence
 └── .env                # Environment config (Hedera + ASI keys)
```

---

## 1️⃣ Evaluator Agent (start local, upgrade to ASI)

* Input: `repo_info` dictionary with fields like `stars`, `commits`, `tests`.
* Output: `{"score": int, "trace": [string list]}`
* **Local version**: rule-based function (Python).
* **Full ASI version**: call ASI:One HTTP API to let an autonomous agent generate the reasoning trace.

### Example (local evaluator)

```python
def evaluate_repo(repo_info):
    score, trace = 0, []
    if repo_info.get("stars", 0) > 50:
        score += 10; trace.append("popular repo: +10")
    if repo_info.get("has_tests", False):
        score += 20; trace.append("has tests: +20")
    commits = repo_info.get("commit_count", 0)
    if commits > 10:
        score += 10; trace.append("active development: +10")
    return {"score": score, "trace": trace}
```

### Example (ASI-integrated evaluator)

```python
import requests, os

def evaluate_repo_with_asi(repo_info):
    api = "https://api.asi1.ai/v1/agent/evaluate"
    headers = {"Authorization": f"Bearer {os.getenv('ASI_API_KEY')}"}
    body = {"repo_info": repo_info}
    r = requests.post(api, headers=headers, json=body)
    return r.json()
```

➡️ The schema is the same, so you can switch implementations easily.

---

## 2️⃣ Hedera Integration

Use Hedera Consensus Service to log the evaluation result.

### Basic steps

1. Create a topic (once).
2. Submit a message `{repo, score, trace_hash}`.

### Example

```python
from hedera import Client, TopicMessageSubmitTransaction, TopicId

def submit_proof(topic_id, message):
    client = Client.for_testnet()
    client.setOperator(os.getenv("HEDERA_OPERATOR_ID"), os.getenv("HEDERA_OPERATOR_KEY"))
    tx = (TopicMessageSubmitTransaction()
          .setTopicId(TopicId.fromString(topic_id))
          .setMessage(message)
          .execute(client))
    receipt = tx.getReceipt(client)
    return str(receipt.transactionId)
```

---

## 3️⃣ FastAPI Endpoints

### `/evaluate` (POST)

* Input: `{"repo_url": "https://github.com/user/repo"}`
* Process:

  * Fetch repo metadata via `github_client`.
  * Call evaluator.
  * Hash reasoning trace (`sha256`).
  * Submit to Hedera.
  * Save and return JSON result.

### `/results/{owner}/{repo}` (GET)

* Fetch stored evaluations for given repo.

### `/create_topic` (POST)

* Admin helper to create Hedera Consensus Topic.

---

## 4️⃣ Data Models (Pydantic)

```python
class EvaluateRequest(BaseModel):
    repo_url: str

class EvaluationResult(BaseModel):
    repo: str
    score: int
    trace: List[str]
    trace_hash: str
    hedera_tx: Optional[str]
    timestamp: datetime
```

---

## 5️⃣ Environment Variables

```
GITHUB_TOKEN=ghp_...
HEDERA_OPERATOR_ID=0.0.xxxx
HEDERA_OPERATOR_KEY=302e02...
HEDERA_TOPIC_ID=0.0.yyyy
ASI_API_KEY=sk_...
```

---

## 6️⃣ Local Storage

Simple JSON file (`storage.json`) to save evaluation records:

```json
[
  {
    "repo": "owner/repo",
    "score": 65,
    "trace": ["has tests +20","10 commits +10"],
    "trace_hash": "abc123",
    "hedera_tx": "0.0.xxxx-0-...",
    "timestamp": "2025-10-16T12:00:00Z"
  }
]
```

---

## 7️⃣ Swagger UI

FastAPI auto-generates `/docs` (Swagger UI).
Use it to:

* POST `/evaluate` → triggers evaluation flow
* GET `/results/{owner}/{repo}` → view results
  No frontend needed.

---

## 8️⃣ Future Upgrades (MVP level)

* Multi-Agent Consensus (two ASI agents debate before writing proof).
* Challenge Flow (`/challenge` endpoint).
* Hedera Token minting (reputation badge).
* Real-time task posting + notifications.

---

## Project Explanation (High-level)

**ProofForge** = "proof forge" - where proofs are forged/created.
It's a platform that connects **human developers** and **AI agents**.
Agents can:

* **analyze code or tasks** (like GitHub PRs),
* **generate reasoning traces** (why they made decisions),
* and **publish verifiable proofs** of those decisions on **Hedera Hashgraph** (so everyone trusts the result).

This makes collaboration between people and autonomous agents **transparent and auditable**.

---

## Example Use Case

A contributor submits a pull request on GitHub.
ProofForge:

1. Fetches that PR data.
2. Uses an **ASI agent** (Evaluator) to review the code, explain its decision, and output a structured reasoning trace (like "+20 for tests," "-10 for style").
3. Sends a **proof** of this reasoning (hash + result) to **Hedera Consensus Service** for public verification.
4. Optionally, issues a reputation token or badge to the contributor.

Everything the agent does is explainable and provable.

---

## Key Technologies (explained simply)

| Layer             | Tech                               | Role                                                                  |
| ----------------- | ---------------------------------- | --------------------------------------------------------------------- |
| **Backend**       | FastAPI                            | Python web server for endpoints (`/evaluate`, `/results`).            |
| **Reasoning**     | ASI:One + MeTTa                    | Defines AI agents that reason symbolically (explainable, rule-based). |
| **Verification**  | Hedera Consensus Service           | Immutable proof store (stores evaluation hash + result).              |
| **Frontend**      | Swagger UI (built-in FastAPI docs) | UI to test APIs without extra frontend code.                          |
| **External APIs** | GitHub REST API                    | Fetch code/PR metadata to evaluate.                                   |
