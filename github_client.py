import requests
import os
from typing import Dict, Any
from models import RepoInfo

def fetch_github_data(owner: str, repo: str) -> RepoInfo:
    """Fetch repository data from GitHub API"""
    headers = {}
    if github_token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {github_token}"
    
    base_url = "https://api.github.com"
    
    try:
        # Fetch repo metadata
        repo_response = requests.get(f"{base_url}/repos/{owner}/{repo}", headers=headers)
        if repo_response.status_code == 404:
            raise ValueError("Repository not found")
        elif repo_response.status_code == 403:
            raise ValueError("Repository access forbidden (may be private)")
        
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
        
        return RepoInfo(
            stars=repo_data.get("stargazers_count", 0),
            open_issues=repo_data.get("open_issues_count", 0),
            has_tests=has_tests,
            commit_count=len(commits_data),
            description=repo_data.get("description", ""),
            language=repo_data.get("language", ""),
            size=repo_data.get("size", 0)
        )
        
    except requests.RequestException as e:
        raise ValueError(f"GitHub API error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error fetching repository data: {str(e)}")

def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo from GitHub URL"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(str(url))
        path = parsed.path.strip('/')
        parts = path.split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            raise ValueError("Invalid GitHub URL format")
    except Exception as e:
        raise ValueError(f"Could not parse GitHub URL: {e}")
