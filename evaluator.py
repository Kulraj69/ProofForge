from typing import Dict, Any, Tuple, List
import requests
import os
import asyncio
from datetime import datetime
from uuid import uuid4
from openai import OpenAI
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

# Initialize ASI client following the same pattern as code.py
def initialize_asi_client():
    """Initialize ASI client with same configuration as code.py"""
    return OpenAI(
        base_url='https://api.asi1.ai/v1',
        api_key=os.getenv('ASI_API_KEY', 'sk_ef5bd03613464e6e8af79d8aa362a1a3f3d8145f5e314bf3af40a37aff301dca')
    )

# Repository quality patterns to detect
REPOSITORY_QUALITY_PATTERNS = {
    "excellent": [
        "comprehensive test coverage",
        "documentation present",
        "active maintenance",
        "good commit history",
        "proper licensing",
        "code quality tools",
        "ci/cd pipeline"
    ],
    "good": [
        "some tests present",
        "basic documentation",
        "recent commits",
        "readme file",
        "issue tracking"
    ],
    "needs_improvement": [
        "no tests found",
        "minimal documentation",
        "inactive repository",
        "poor commit messages",
        "no license"
    ]
}

def analyze_repository_quality(repo_info: RepoInfo) -> str:
    """Analyze repository for quality patterns"""
    quality_indicators = []
    
    # Check for test presence
    if repo_info.has_tests:
        quality_indicators.append("comprehensive test coverage")
    else:
        quality_indicators.append("no tests found")
    
    # Check for activity
    if repo_info.commit_count >= 100:
        quality_indicators.append("active maintenance")
    elif repo_info.commit_count >= 10:
        quality_indicators.append("recent commits")
    else:
        quality_indicators.append("inactive repository")
    
    # Check for popularity
    if repo_info.stars >= 1000:
        quality_indicators.append("high community adoption")
    elif repo_info.stars >= 100:
        quality_indicators.append("moderate community interest")
    else:
        quality_indicators.append("limited community engagement")
    
    # Check for issues management
    if repo_info.open_issues == 0:
        quality_indicators.append("well-maintained")
    elif repo_info.open_issues <= 10:
        quality_indicators.append("some technical debt")
    else:
        quality_indicators.append("significant technical debt")
    
    return format_quality_analysis(quality_indicators)

def format_quality_analysis(indicators: List[str]) -> str:
    """Format the repository quality analysis"""
    if not indicators:
        return "Repository quality analysis completed."
    
    analysis = "📊 REPOSITORY QUALITY ANALYSIS:\n\n"
    
    for indicator in indicators:
        if "comprehensive" in indicator or "active" in indicator or "high" in indicator or "well-maintained" in indicator:
            analysis += f"✅ {indicator}\n"
        elif "moderate" in indicator or "some" in indicator or "recent" in indicator:
            analysis += f"⚠️  {indicator}\n"
        else:
            analysis += f"❌ {indicator}\n"
    
    return analysis

def get_quality_score(indicators: List[str]) -> int:
    """Calculate quality score based on indicators"""
    score = 0
    
    for indicator in indicators:
        if "comprehensive" in indicator or "active" in indicator or "high" in indicator or "well-maintained" in indicator:
            score += 25
        elif "moderate" in indicator or "some" in indicator or "recent" in indicator:
            score += 15
        else:
            score += 5
    
    return min(score, 100)  # Cap at 100

async def perform_comprehensive_repo_analysis(repo_info: RepoInfo) -> str:
    """Perform comprehensive repository analysis with ASI"""
    
    try:
        # Initialize ASI client
        client = initialize_asi_client()
        
        # Perform traditional quality analysis
        quality_analysis = analyze_repository_quality(repo_info)
        
        # Generate AI-powered detailed analysis
        ai_analysis = await generate_ai_repo_analysis(client, repo_info, quality_analysis)
        
        # Format comprehensive report
        report = f"""🔍 COMPREHENSIVE REPOSITORY ANALYSIS REPORT

═══════════════════════════════════════════════════════════════

📊 REPOSITORY METRICS:
- Stars: {repo_info.stars}
- Open Issues: {repo_info.open_issues}
- Commit Count: {repo_info.commit_count}
- Has Tests: {repo_info.has_tests}
- Language: {repo_info.language or 'Not specified'}
- Size: {repo_info.size} KB

═══════════════════════════════════════════════════════════════

{quality_analysis}

═══════════════════════════════════════════════════════════════

🤖 DETAILED AI ANALYSIS:
{ai_analysis}

═══════════════════════════════════════════════════════════════

💡 RECOMMENDATIONS:
1. Improve test coverage if lacking
2. Address open issues and technical debt
3. Enhance documentation and README
4. Implement CI/CD pipeline
5. Add proper licensing and contribution guidelines

This analysis was performed by the ProofForge Repository Analyzer Agent 🤖"""

        return report
        
    except Exception as e:
        return f"Error during comprehensive analysis: {str(e)}"

async def generate_ai_repo_analysis(client: OpenAI, repo_info: RepoInfo, quality_analysis: str) -> str:
    """Generate AI-powered detailed repository analysis"""
    
    try:
        response = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": """
You are an expert repository analyst specializing in code quality assessment and project evaluation.

When analyzing repositories, provide:
1. OVERALL ASSESSMENT: Repository quality score (0-100) with justification
2. STRENGTHS: What the repository does well
3. WEAKNESSES: Areas that need improvement
4. RECOMMENDATIONS: Specific actionable steps to improve the repository
5. COMMUNITY IMPACT: Assessment of community engagement and adoption potential

Focus on:
- Code quality and maintainability
- Test coverage and reliability
- Documentation and accessibility
- Community engagement and adoption
- Development practices and workflows
- Security and best practices

Provide actionable, specific recommendations for improvement.
                """},
                {"role": "user", "content": f"""
Repository Information:
- Stars: {repo_info.stars}
- Open Issues: {repo_info.open_issues}
- Commit Count: {repo_info.commit_count}
- Has Tests: {repo_info.has_tests}
- Language: {repo_info.language or 'Not specified'}
- Size: {repo_info.size} KB
- Description: {repo_info.description or 'No description'}

Quality Analysis:
{quality_analysis}

Please provide a detailed analysis of this repository's quality and recommendations for improvement.
                """},
            ],
            max_tokens=1024,
        )

        return str(response.choices[0].message.content)
        
    except Exception as e:
        return f"Unable to generate AI analysis: {str(e)}"

async def evaluate_repo_with_asi(repo_info: RepoInfo) -> Dict[str, Any]:
    """ASI-integrated evaluator following the same pattern as code.py"""
    try:
        # Perform comprehensive analysis
        analysis_report = await perform_comprehensive_repo_analysis(repo_info)
        
        # Calculate score based on repository metrics
        quality_indicators = []
        
        # Stars contribution
        if repo_info.stars >= 1000:
            quality_indicators.append("high community adoption")
        elif repo_info.stars >= 100:
            quality_indicators.append("moderate community interest")
        else:
            quality_indicators.append("limited community engagement")
        
        # Test presence
        if repo_info.has_tests:
            quality_indicators.append("comprehensive test coverage")
        else:
            quality_indicators.append("no tests found")
        
        # Activity level
        if repo_info.commit_count >= 100:
            quality_indicators.append("active maintenance")
        elif repo_info.commit_count >= 10:
            quality_indicators.append("recent commits")
        else:
            quality_indicators.append("inactive repository")
        
        # Issues management
        if repo_info.open_issues == 0:
            quality_indicators.append("well-maintained")
        elif repo_info.open_issues <= 10:
            quality_indicators.append("some technical debt")
        else:
            quality_indicators.append("significant technical debt")
        
        # Calculate score
        score = get_quality_score(quality_indicators)
        
        # Create trace with detailed analysis
        trace = [
            f"Repository analysis completed: {score}/100",
            f"Community engagement: {repo_info.stars} stars",
            f"Development activity: {repo_info.commit_count} commits",
            f"Test coverage: {'Present' if repo_info.has_tests else 'Missing'}",
            f"Issue management: {repo_info.open_issues} open issues"
        ]
        
        return {
            "score": score,
            "trace": trace,
            "analysis_report": analysis_report
        }
        
    except Exception as e:
        # Fallback to local evaluator on any error
        print(f"ASI evaluation failed: {str(e)}, falling back to local evaluator")
        score, trace = evaluate_repo_local(repo_info)
        return {"score": score, "trace": trace}

async def evaluate_repo(repo_info: RepoInfo, use_asi: bool = False) -> Dict[str, Any]:
    """Main evaluation function that can use local or ASI evaluator"""
    if use_asi and os.getenv("ASI_API_KEY"):
        return await evaluate_repo_with_asi(repo_info)
    else:
        score, trace = evaluate_repo_local(repo_info)
        return {"score": score, "trace": trace}
