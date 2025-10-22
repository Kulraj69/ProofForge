from typing import Dict, Any, Tuple, List
import requests
import os
from models import RepoInfo

def evaluate_repo_local(repo_info: RepoInfo) -> Tuple[int, List[str]]:
    """Local rule-based evaluator that returns score and trace"""
    score = 0
    trace = []
    
    # Stars contribution
    stars = repo_info.stars
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
    if repo_info.has_tests:
        score += 25
        trace.append("Has tests: +25")
    else:
        trace.append("No tests found: +0")
    
    # Active development (recent commits)
    commit_count = repo_info.commit_count
    if commit_count >= 100:
        score += 20
        trace.append(f"High activity ({commit_count} commits): +20")
    elif commit_count >= 10:
        score += 10
        trace.append(f"Some activity ({commit_count} commits): +10")
    else:
        trace.append(f"Low activity ({commit_count} commits): +0")
    
    # Issues management
    open_issues = repo_info.open_issues
    if open_issues == 0:
        score += 15
        trace.append("No open issues: +15")
    elif open_issues <= 10:
        score += 5
        trace.append(f"Few open issues ({open_issues}): +5")
    else:
        trace.append(f"Many open issues ({open_issues}): +0")
    
    # Language bonus
    if repo_info.language:
        score += 5
        trace.append(f"Has language ({repo_info.language}): +5")
    
    # Repository size consideration
    if repo_info.size:
        if repo_info.size > 10000:
            score += 10
            trace.append(f"Large codebase ({repo_info.size} KB): +10")
        elif repo_info.size > 1000:
            score += 5
            trace.append(f"Medium codebase ({repo_info.size} KB): +5")
    
    return score, trace

def evaluate_repo_with_asi(repo_info: RepoInfo) -> Dict[str, Any]:
    """ASI-integrated evaluator that calls ASI:One API"""
    try:
        api = "https://api.asi1.ai/v1/agent/evaluate"
        headers = {"Authorization": f"Bearer {os.getenv('ASI_API_KEY')}"}
        
        # Convert RepoInfo to dict for API call
        repo_data = repo_info.dict()
        
        response = requests.post(api, headers=headers, json={"repo_info": repo_data})
        
        if response.status_code == 200:
            result = response.json()
            return {
                "score": result.get("score", 0),
                "trace": result.get("trace", [])
            }
        else:
            # Fallback to local evaluator if ASI fails
            print(f"ASI API failed with status {response.status_code}, falling back to local evaluator")
            score, trace = evaluate_repo_local(repo_info)
            return {"score": score, "trace": trace}
            
    except Exception as e:
        # Fallback to local evaluator on any error
        print(f"ASI evaluation failed: {str(e)}, falling back to local evaluator")
        score, trace = evaluate_repo_local(repo_info)
        return {"score": score, "trace": trace}

def evaluate_repo(repo_info: RepoInfo, use_asi: bool = False) -> Dict[str, Any]:
    """Main evaluation function that can use local or ASI evaluator"""
    if use_asi and os.getenv("ASI_API_KEY"):
        return evaluate_repo_with_asi(repo_info)
    else:
        score, trace = evaluate_repo_local(repo_info)
        return {"score": score, "trace": trace}
