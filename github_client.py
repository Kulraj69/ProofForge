import requests
import os
import asyncio
import aiohttp
from typing import Dict, Any
from models import RepoInfo
from cache import github_cache, generate_cache_key

def fetch_github_data(owner: str, repo: str) -> RepoInfo:
    """Fetch repository data from GitHub API with caching"""
    cache_key = generate_cache_key(owner, repo)
    
    # Check cache first
    cached_data = github_cache.get(cache_key)
    if cached_data:
        return RepoInfo(**cached_data)
    
    headers = {}
    if github_token := os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {github_token}"
    
    base_url = "https://api.github.com"
    
    try:
        # Use session for connection pooling
        with requests.Session() as session:
            session.headers.update(headers)
            
            # Fetch repo metadata
            repo_response = session.get(f"{base_url}/repos/{owner}/{repo}", timeout=10)
            if repo_response.status_code == 404:
                raise ValueError("Repository not found")
            elif repo_response.status_code == 403:
                raise ValueError("Repository access forbidden (may be private)")
            
            repo_data = repo_response.json()
            
            # Fetch commits (limit to recent commits for performance)
            commits_response = session.get(
                f"{base_url}/repos/{owner}/{repo}/commits", 
                params={"per_page": 100},  # Limit to 100 recent commits
                timeout=10
            )
            commits_data = commits_response.json() if commits_response.status_code == 200 else []
            
            # Check for tests directory
            contents_response = session.get(f"{base_url}/repos/{owner}/{repo}/contents", timeout=10)
            has_tests = False
            if contents_response.status_code == 200:
                contents = contents_response.json()
                has_tests = any(item["name"].lower() in ["tests", "test"] and item["type"] == "dir" for item in contents)
            
            repo_info = RepoInfo(
                stars=repo_data.get("stargazers_count", 0),
                open_issues=repo_data.get("open_issues_count", 0),
                has_tests=has_tests,
                commit_count=len(commits_data),
                description=repo_data.get("description", ""),
                language=repo_data.get("language", ""),
                size=repo_data.get("size", 0)
            )
            
            # Cache the result
            github_cache.set(cache_key, repo_info.dict())
            
            return repo_info
        
    except requests.RequestException as e:
        raise ValueError(f"GitHub API error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error fetching repository data: {str(e)}")

def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo from GitHub URL with caching"""
    try:
        from cache import cached_parse_github_url
        return cached_parse_github_url(str(url))
    except Exception as e:
        raise ValueError(f"Could not parse GitHub URL: {e}")
