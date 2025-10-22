import re
from typing import Optional
from urllib.parse import urlparse

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_github_url(url: str) -> bool:
    """Validate GitHub URL format"""
    try:
        parsed = urlparse(url)
        if parsed.netloc not in ['github.com', 'www.github.com']:
            return False
        
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            return False
        
        # Check if owner and repo names are valid
        owner, repo = path_parts[0], path_parts[1]
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', owner):
            return False
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$', repo):
            return False
        
        return True
    except Exception:
        return False

def validate_hedera_credentials(operator_id: str, operator_key: str) -> bool:
    """Validate Hedera credentials format"""
    try:
        # Basic format validation for Hedera credentials
        if not operator_id or not operator_key:
            return False
        
        # Check operator ID format (0.0.xxxx)
        if not re.match(r'^\d+\.\d+\.\d+$', operator_id):
            return False
        
        # Check if key is hex string
        if not re.match(r'^[0-9a-fA-F]+$', operator_key):
            return False
        
        return True
    except Exception:
        return False

def validate_repo_name(owner: str, repo: str) -> bool:
    """Validate repository owner and name"""
    try:
        # GitHub username validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$', owner):
            return False
        
        # GitHub repository name validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$', repo):
            return False
        
        return True
    except Exception:
        return False

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()
