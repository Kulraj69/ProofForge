from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import List
import hashlib
import json
import os
from dotenv import load_dotenv

from models import EvaluateRequest, EvaluationResult, CreateTopicRequest
from github_client import fetch_github_data, parse_github_url
from evaluator import evaluate_repo
from hedera_client import submit_proof, create_consensus_topic, get_hedera_explorer_url
from storage import save_evaluation, get_evaluations_by_repo, get_all_evaluations

load_dotenv()

app = FastAPI(
    title="ProofForge",
    description="Evaluate GitHub repos and anchor explainable evaluation on Hedera testnet",
    version="1.0.0"
)


def generate_trace_hash(trace: List[str]) -> str:
    """Generate SHA256 hash of trace"""
    trace_str = json.dumps(trace, sort_keys=True)
    return hashlib.sha256(trace_str.encode()).hexdigest()

@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate_repository(request: EvaluateRequest):
    """Evaluate a GitHub repository and submit proof to Hedera"""
    try:
        # Parse GitHub URL
        owner, repo = parse_github_url(str(request.repo_url))
        repo_name = f"{owner}/{repo}"
        
        # Fetch GitHub data
        repo_info = fetch_github_data(owner, repo)
        
        # Run evaluation (with ASI if available)
        use_asi = bool(os.getenv("ASI_API_KEY"))
        evaluation = evaluate_repo(repo_info, use_asi=use_asi)
        score = evaluation["score"]
        trace = evaluation["trace"]
        
        # Generate trace hash
        trace_hash = generate_trace_hash(trace)
        
        # Create timestamp
        timestamp = datetime.now()
        
        # Submit to Hedera
        topic_id = os.getenv("HEDERA_TOPIC_ID", "default_topic")
        hedera_message = {
            "repo": repo_name,
            "score": score,
            "trace_hash": trace_hash,
            "timestamp": timestamp.isoformat()
        }
        
        hedera_tx_id = submit_proof(topic_id, hedera_message)
        
        # Create result
        result = EvaluationResult(
            repo=repo_name,
            score=score,
            trace=trace,
            trace_hash=trace_hash,
            hedera_tx=hedera_tx_id,
            timestamp=timestamp
        )
        
        # Save to storage
        save_evaluation(result.dict())
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/results/{owner}/{repo}", response_model=List[EvaluationResult])
async def get_repository_results(owner: str, repo: str):
    """Get all evaluation results for a specific repository"""
    try:
        results = get_evaluations_by_repo(owner, repo)
        return [EvaluationResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")

@app.get("/results", response_model=List[EvaluationResult])
async def get_all_results():
    """Get all evaluation results"""
    try:
        results = get_all_evaluations()
        return [EvaluationResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")

@app.post("/create_topic")
async def create_hedera_topic(request: CreateTopicRequest):
    """Create a new Hedera Consensus Topic"""
    try:
        topic_id = create_consensus_topic(request.topic_memo)
        if topic_id:
            return {"topic_id": topic_id, "message": "Topic created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create topic")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating topic: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ProofForge API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
