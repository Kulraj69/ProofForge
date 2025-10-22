import json
import os
import threading
from typing import List, Dict, Any
from datetime import datetime

STORAGE_FILE = "storage.json"
_storage_lock = threading.Lock()

def ensure_storage_exists():
    """Ensure storage.json exists with empty array"""
    if not os.path.exists(STORAGE_FILE):
        save_storage([])

def load_storage() -> List[Dict[str, Any]]:
    """Load evaluation results from storage file"""
    ensure_storage_exists()
    
    try:
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_storage(data: List[Dict[str, Any]]) -> None:
    """Save evaluation results to storage file with thread safety"""
    try:
        with _storage_lock:
            # Create backup before writing
            if os.path.exists(STORAGE_FILE):
                backup_file = f"{STORAGE_FILE}.backup"
                with open(STORAGE_FILE, 'r') as src, open(backup_file, 'w') as dst:
                    dst.write(src.read())
            
            # Write new data
            with open(STORAGE_FILE, 'w') as f:
                json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"Failed to save storage: {str(e)}")
        # Restore from backup if available
        backup_file = f"{STORAGE_FILE}.backup"
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r') as src, open(STORAGE_FILE, 'w') as dst:
                    dst.write(src.read())
            except Exception:
                pass

def save_evaluation(result: Dict[str, Any]) -> None:
    """Save a single evaluation result"""
    ensure_storage_exists()
    storage = load_storage()
    storage.append(result)
    save_storage(storage)

def get_evaluations_by_repo(owner: str, repo: str) -> List[Dict[str, Any]]:
    """Get all evaluations for a specific repository"""
    storage = load_storage()
    repo_name = f"{owner}/{repo}"
    return [eval_result for eval_result in storage if eval_result.get("repo") == repo_name]

def get_all_evaluations() -> List[Dict[str, Any]]:
    """Get all stored evaluations"""
    return load_storage()

def clear_storage() -> None:
    """Clear all stored evaluations"""
    save_storage([])
