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
from hedera_client import submit_proof, create_consensus_topic, get_hedera_explorer_url, submit_message
from ipfs_client import upload_to_ipfs, get_from_ipfs, get_ipfs_url
from storage import save_evaluation, get_evaluations_by_repo, get_all_evaluations
from config import Config
from logger import logger
from validators import validate_github_url, validate_repo_name, sanitize_input
from monitoring import monitor_performance, get_performance_metrics

load_dotenv()

app = FastAPI(
    title="ProofForge",
    description="Evaluate GitHub repos and anchor explainable evaluation on Hedera testnet",
    version="1.0.0"
)

# Validate configuration on startup
Config.validate_config()


def generate_trace_hash(trace: List[str]) -> str:
    """Generate SHA256 hash of trace"""
    trace_str = json.dumps(trace, sort_keys=True)
    return hashlib.sha256(trace_str.encode()).hexdigest()

@app.post("/evaluate", response_model=EvaluationResult)
@monitor_performance
async def evaluate_repository(request: EvaluateRequest):
    """Evaluate a GitHub repository and submit proof to Hedera"""
    try:
        logger.info(f"Starting evaluation for repository: {request.repo_url}")
        
        # Validate GitHub URL
        if not validate_github_url(str(request.repo_url)):
            raise HTTPException(status_code=400, detail="Invalid GitHub URL format")
        
        # Parse GitHub URL
        owner, repo = parse_github_url(str(request.repo_url))
        
        # Validate repository name
        if not validate_repo_name(owner, repo):
            raise HTTPException(status_code=400, detail="Invalid repository name format")
        
        repo_name = f"{owner}/{repo}"
        logger.info(f"Parsed repository: {repo_name}")
        
        # Fetch GitHub data
        logger.info("Fetching GitHub repository data...")
        repo_info = fetch_github_data(owner, repo)
        logger.info(f"Repository data fetched: {repo_info.stars} stars, {repo_info.commit_count} commits")
        
        # Run evaluation (with ASI if available)
        use_asi = bool(Config.ASI_API_KEY)
        logger.info(f"Running evaluation with ASI: {use_asi}")
        evaluation = await evaluate_repo(repo_info, use_asi=use_asi)
        score = evaluation["score"]
        trace = evaluation["trace"]
        logger.info(f"Evaluation completed: score={score}, trace={len(trace)} items")
        
        # Generate trace hash
        trace_hash = generate_trace_hash(trace)
        logger.info(f"Generated trace hash: {trace_hash[:16]}...")
        
        # Create timestamp
        timestamp = datetime.now()
        
        # Submit to Hedera
        logger.info("Submitting proof to Hedera...")
        hedera_message = {
            "repo": repo_name,
            "score": score,
            "trace_hash": trace_hash,
            "timestamp": timestamp.isoformat()
        }
        
        hedera_tx_id = submit_proof(Config.HEDERA_TOPIC_ID, hedera_message)
        logger.info(f"Hedera transaction ID: {hedera_tx_id}")
        
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
        logger.info("Evaluation result saved to storage")
        
        # Optional: Upload to IPFS for decentralized storage
        try:
            ipfs_hash = upload_to_ipfs(result.dict())
            if ipfs_hash:
                logger.info(f"Result uploaded to IPFS: {ipfs_hash}")
                # Add IPFS hash to result
                result_dict = result.dict()
                result_dict['ipfs_hash'] = ipfs_hash
                result_dict['ipfs_url'] = get_ipfs_url(ipfs_hash)
        except Exception as e:
            logger.warning(f"IPFS upload failed: {str(e)}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
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

@app.post("/submit_to_hedera")
async def submit_to_hedera_endpoint(message: dict):
    """Low-level helper: sends arbitrary JSON message to Hedera topic"""
    try:
        logger.info(f"Submitting message to Hedera: {message}")
        topic_id = Config.HEDERA_TOPIC_ID
        tx_id = submit_proof(topic_id, message)
        logger.info(f"Hedera transaction ID: {tx_id}")
        return {
            "message": "Message submitted to Hedera successfully",
            "transaction_id": tx_id,
            "topic_id": topic_id
        }
    except Exception as e:
        logger.error(f"Error submitting to Hedera: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting to Hedera: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "ProofForge API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/metrics")
async def get_metrics():
    """Get performance metrics"""
    return get_performance_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
