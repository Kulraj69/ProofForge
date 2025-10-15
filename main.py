from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import requests
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="CodeRepute",
    description="Evaluate GitHub repos and anchor explainable evaluation on Hedera testnet",
    version="1.0.0"
)

class RepoEvaluationRequest(BaseModel):
    repo_url: HttpUrl

class RepoEvaluationResponse(BaseModel):
    repo: str
    score: int
    trace: List[str]
    trace_hash: str
    hedera_tx_id: str
    timestamp: str

def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo from GitHub URL"""
    try:
        path = url.path.strip('/')
        parts = path.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            raise ValueError("Invalid GitHub URL format")
    except Exception as e:
        raise ValueError(f"Could not parse GitHub URL: {e}")

def fetch_github_data(owner: str, repo: str) -> Dict[str, Any]:
    """Fetch repository data from GitHub API"""
    headers = {}
    if github_token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {github_token}"
    
    base_url = "https://api.github.com"
    
    # Fetch repo metadata
    repo_response = requests.get(f"{base_url}/repos/{owner}/{repo}", headers=headers)
    if repo_response.status_code == 404:
        raise HTTPException(status_code=404, detail="Repository not found")
    elif repo_response.status_code == 403:
        raise HTTPException(status_code=403, detail="Repository access forbidden (may be private)")
    
    repo_data = repo_response.json()
    
    # Fetch commits
    commits_response = requests.get(f"{base_url}/repos/{owner}/{repo}/commits", headers=headers)
    commits_data = commits_response.json() if commits_response.status_code == 200 else []
    
    # Check for tests directory
    contents_response = requests.get(f"{base_url}/repos/{owner}/{repo}/contents", headers=headers)
    has_tests = False
    if contents_response.status_code == 200:
        contents = contents_response.json()
        has_tests = any(item["name"].lower() in ["tests", "test"] and item["type"] == "dir" for item in contents)
    
    return {
        "stars": repo_data.get("stargazers_count", 0),
        "open_issues": repo_data.get("open_issues_count", 0),
        "has_tests": has_tests,
        "commit_count": len(commits_data),
        "description": repo_data.get("description", ""),
        "language": repo_data.get("language", ""),
        "size": repo_data.get("size", 0)
    }

def evaluate_repo_summary(summary: Dict[str, Any]) -> tuple[int, List[str]]:
    """Simple evaluator that returns score and trace"""
    score = 0
    trace = []
    
    # Stars contribution
    stars = summary["stars"]
    if stars >= 1000:
        score += 50
        trace.append(f"High stars (1000+): +50")
    elif stars >= 100:
        score += 30
        trace.append(f"Good stars ({stars}): +30")
    elif stars >= 10:
        score += 15
        trace.append(f"Some stars ({stars}): +15")
    else:
        trace.append(f"Low stars ({stars}): +0")
    
    # Test presence
    if summary["has_tests"]:
        score += 25
        trace.append("Has tests: +25")
    else:
        trace.append("No tests found: +0")
    
    # Active development (recent commits)
    commit_count = summary["commit_count"]
    if commit_count >= 100:
        score += 20
        trace.append(f"High activity ({commit_count} commits): +20")
    elif commit_count >= 10:
        score += 10
        trace.append(f"Some activity ({commit_count} commits): +10")
    else:
        trace.append(f"Low activity ({commit_count} commits): +0")
    
    # Issues management
    open_issues = summary["open_issues"]
    if open_issues == 0:
        score += 15
        trace.append("No open issues: +15")
    elif open_issues <= 10:
        score += 5
        trace.append(f"Few open issues ({open_issues}): +5")
    else:
        trace.append(f"Many open issues ({open_issues}): +0")
    
    # Language bonus
    if summary["language"]:
        score += 5
        trace.append(f"Has language ({summary['language']}): +5")
    
    return score, trace

def generate_trace_hash(trace: List[str]) -> str:
    """Generate SHA256 hash of trace"""
    trace_str = json.dumps(trace, sort_keys=True)
    return hashlib.sha256(trace_str.encode()).hexdigest()

def submit_to_hedera(repo: str, score: int, trace_hash: str, timestamp: str) -> str:
    """Submit proof to Hedera (placeholder implementation)"""
    # This is a placeholder - in real implementation, you would:
    # 1. Connect to Hedera testnet
    # 2. Submit message to consensus topic
    # 3. Return transaction ID
    
    message = {
        "repo": repo,
        "score": score,
        "trace_hash": trace_hash,
        "timestamp": timestamp
    }
    
    # For now, return a mock transaction ID
    # In production, this would be the actual Hedera transaction ID
    return f"0.0.123456@{int(datetime.now().timestamp())}.123456789"

@app.post("/evaluate", response_model=RepoEvaluationResponse)
async def evaluate_repository(request: RepoEvaluationRequest):
    """Evaluate a GitHub repository and submit proof to Hedera"""
    try:
        # Parse GitHub URL
        owner, repo = parse_github_url(str(request.repo_url))
        repo_name = f"{owner}/{repo}"
        
        # Fetch GitHub data
        summary = fetch_github_data(owner, repo)
        
        # Run evaluation
        score, trace = evaluate_repo_summary(summary)
        
        # Generate trace hash
        trace_hash = generate_trace_hash(trace)
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Submit to Hedera (placeholder)
        hedera_tx_id = submit_to_hedera(repo_name, score, trace_hash, timestamp)
        
        return RepoEvaluationResponse(
            repo=repo_name,
            score=score,
            trace=trace,
            trace_hash=trace_hash,
            hedera_tx_id=hedera_tx_id,
            timestamp=timestamp
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "CodeRepute API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
