"""
Repository Evaluator Agent - Following code.py pattern for repository analysis
This agent provides comprehensive repository quality assessment using ASI integration
"""

from datetime import datetime
from uuid import uuid4
import asyncio
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openai import OpenAI
from uagents import Context, Protocol, Agent, Model
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Import our repository analysis components
from models import RepoInfo
from evaluator import perform_comprehensive_repo_analysis, analyze_repository_quality
from github_client import fetch_github_data, parse_github_url

### Comprehensive Repository Analysis Agent with ASI Integration

## This agent provides comprehensive repository quality assessment including
## code quality analysis, community engagement evaluation, and development practices review

# the subject that this assistant is an expert in
subject_matter = "comprehensive repository quality assessment and code evaluation"

client = OpenAI(
    # By default, we are using the ASI-1 LLM endpoint and model
    base_url='https://api.asi1.ai/v1',
    # You can get an ASI-1 api key by creating an account at https://asi1.ai/dashboard/api-keys
    api_key=os.getenv('ASI_API_KEY', 'sk_ef5bd03613464e6e8af79d8aa362a1a3f3d8145f5e314bf3af40a37aff301dca'),
)

agent = Agent(
    name="repository_evaluator",
    seed="repository_evaluator_unique_seed_2024"
)

# We create a new protocol which is compatible with the chat protocol spec
protocol = Protocol(spec=chat_protocol_spec)

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

def is_github_url(text: str) -> bool:
    """Check if the input looks like a GitHub URL"""
    github_indicators = [
        "github.com",
        "https://github.com/",
        "http://github.com/",
        "git@github.com:"
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in github_indicators)

def extract_repo_info_from_url(url: str) -> tuple:
    """Extract owner and repo from GitHub URL"""
    try:
        return parse_github_url(url)
    except Exception:
        return None, None

async def perform_repository_analysis(ctx: Context, repo_url: str) -> str:
    """Perform comprehensive repository analysis"""
    
    try:
        # Extract repository information
        owner, repo = extract_repo_info_from_url(repo_url)
        
        if not owner or not repo:
            return "❌ Invalid GitHub URL. Please provide a valid GitHub repository URL."
        
        # Fetch repository data
        repo_info = fetch_github_data(owner, repo)
        
        # Perform comprehensive analysis
        analysis_report = await perform_comprehensive_repo_analysis(repo_info)
        
        return analysis_report
        
    except Exception as e:
        ctx.logger.exception('Error during repository analysis')
        return f"❌ Error during repository analysis: {str(e)}"

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

# We define the handler for the chat messages that are sent to your agent
@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    # send the acknowledgement for receiving the message
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.now(), acknowledged_msg_id=msg.msg_id),
    )

    # collect up all the text chunks
    text = ''
    for item in msg.content:
        if isinstance(item, TextContent):
            text += item.text

    # Check if this looks like a GitHub URL
    if not is_github_url(text):
        response = """🤖 I'm a Repository Quality Analyzer with ASI Integration!

I can provide:
• 🔍 Comprehensive Repository Quality Assessment
• 📊 Code Quality and Maintainability Analysis
• ⭐ Community Engagement Evaluation
• 🧪 Test Coverage and Reliability Assessment
• 📝 Documentation Quality Review
• 🚀 Development Practices Analysis
• 🛡️ Security and Best Practices Assessment

Please send me a GitHub repository URL for comprehensive quality analysis!

Example URLs I can analyze:
• https://github.com/owner/repository
• https://github.com/microsoft/vscode
• https://github.com/facebook/react

I'll provide detailed insights including:
• Overall quality score (0-100)
• Strengths and weaknesses
• Specific improvement recommendations
• Community engagement assessment
• Development practices evaluation"""
    else:
        # Perform comprehensive repository analysis
        response = await perform_repository_analysis(ctx, text)
    
    # send the response back to the user
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=response),
        ]
    ))

@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    # we are not interested in the acknowledgements for this example, but they can be useful to
    # implement read receipts, for example.
    pass

# attach the protocol to the agent
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
