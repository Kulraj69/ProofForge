# ProofForge — Application Flow

## Actors

* **User**: provides GitHub repo link.
* **FastAPI Backend**: orchestrator, integrates ASI + Hedera.
* **EvaluatorAgent**: analyzes code & explains reasoning.
* **Hedera Network**: stores verifiable proof (trace hash).
* **Storage**: local JSON file or database.

## Step-by-Step Flow

### 1️⃣ User Input

User opens Swagger UI → `POST /evaluate` → enters JSON:

```json
{"repo_url": "https://github.com/user/project"}
```

### 2️⃣ Backend Extracts Repo Info

* Parses owner/repo from URL.
* Fetches GitHub data:

  * stars, issues, commits, test folders.

### 3️⃣ EvaluatorAgent Reasoning

* Passes metadata to `evaluate_repo()` or `evaluate_repo_with_asi()`.
* Agent returns:

```json
{
  "score": 75,
  "trace": [
    "found tests: +20",
    "stars>50: +10",
    "active commits: +15"
  ]
}
```

### 4️⃣ Create Reasoning Hash

* Convert trace list → JSON string → SHA256 hash.

### 5️⃣ Publish Proof to Hedera

* Message:

```json
{
  "repo":"user/project",
  "score":75,
  "trace_hash":"0xabc...",
  "timestamp":"2025-10-16T12:00:00Z"
}
```

* Sent via `hedera_client.submit_proof()`.
* Hedera returns `transaction_id`.

### 6️⃣ Save Result Locally

Append record to `storage.json` with all fields.

### 7️⃣ Response to User

FastAPI returns:

```json
{
  "repo": "user/project",
  "score": 75,
  "trace": ["found tests +20", "active commits +15"],
  "trace_hash": "0xabc...",
  "hedera_tx": "0.0.xxxx-0-...",
  "timestamp": "2025-10-16T12:00:00Z"
}
```

### 8️⃣ View Results

* User visits `/docs` → GET `/results/{owner}/{repo}`
* Displays all stored evaluations.

---

## MVP Flow (when ASI added)

```
User
 ↓
FastAPI
 ↓
EvaluatorAgent (ASI reasoning → returns score+trace)
 ↓
VerifierAgent (validates reasoning)
 ↓
Hedera (writes trace hash proof)
 ↓
User sees reasoning + Hedera tx link
```

---

## Error & Safety Handling

* If GitHub API fails → return 404.
* If Hedera submission fails → log and return partial result.
* Never log private keys; use env vars.

---

## Demo Script (for hackathon)

1. Go to Swagger UI → `/evaluate`.
2. Paste a GitHub repo.
3. Show returned reasoning trace.
4. Click Hedera tx link → opens in Hedera testnet explorer.
5. Judges see reasoning → on-chain proof.

---

## Summary

**Prototype Flow:**
Human → Evaluator → Hedera → Proof

**MVP Flow:**
Human ↔ Multi-Agent Reasoning (ASI) ↔ Hedera Proof + Tokens
