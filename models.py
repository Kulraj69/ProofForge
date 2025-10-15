from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class EvaluateRequest(BaseModel):
    repo_url: HttpUrl

class EvaluationResult(BaseModel):
    repo: str
    score: int
    trace: List[str]
    trace_hash: str
    hedera_tx: Optional[str]
    timestamp: datetime

class RepoInfo(BaseModel):
    stars: int
    open_issues: int
    has_tests: bool
    commit_count: int
    description: Optional[str] = None
    language: Optional[str] = None
    size: Optional[int] = None

class CreateTopicRequest(BaseModel):
    topic_memo: Optional[str] = "ProofForge Evaluation Topic"
