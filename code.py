from datetime import datetime
from uuid import uuid4
import asyncio

from openai import OpenAI
from uagents import Context, Protocol, Agent, Model
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Removed MeTTa knowledge base dependency for simplicity

### Comprehensive Security Analysis Agent

## This agent provides comprehensive smart contract security analysis including
## vulnerability detection, code review, and security recommendations

# the subject that this assistant is an expert in
subject_matter = "comprehensive smart contract security analysis and vulnerability detection"

client = OpenAI(
    # By default, we are using the ASI-1 LLM endpoint and model
    base_url='https://api.asi1.ai/v1',

    # You can get an ASI-1 api key by creating an account at https://asi1.ai/dashboard/api-keys
    api_key='sk_ef5bd03613464e6e8af79d8aa362a1a3f3d8145f5e314bf3af40a37aff301dca',
)

agent = Agent(
    name="security_analyzer",
    seed="security_analyzer_unique_seed_2024"
)

# We create a new protocol which is compatible with the chat protocol spec
protocol = Protocol(spec=chat_protocol_spec)

# Removed MeTTa knowledge base initialization

# Common vulnerability patterns to detect
VULNERABILITY_PATTERNS = {
    "reentrancy": [
        "external call before state change",
        "msg.sender.call()",
        "delegatecall",
        "state variable not updated before external call"
    ],
    "integer_overflow": [
        "unchecked arithmetic",
        "SafeMath not used",
        "uint256 overflow",
        "unchecked add/sub/mul"
    ],
    "access_control": [
        "missing onlyOwner modifier",
        "public function without access control",
        "tx.origin usage",
        "missing role-based access"
    ],
    "unchecked_calls": [
        "call() without checking return value",
        "send() without checking return",
        "delegatecall without verification"
    ],
    "front_running": [
        "price manipulation",
        "MEV vulnerability",
        "transaction ordering dependency"
    ]
}

def analyze_vulnerabilities(code: str) -> str:
    """Analyze code for common vulnerability patterns"""
    vulnerabilities_found = []
    
    code_lower = code.lower()
    
    for vuln_type, patterns in VULNERABILITY_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in code_lower:
                vulnerabilities_found.append({
                    "type": vuln_type,
                    "pattern": pattern,
                    "severity": get_severity(vuln_type)
                })
    
    return format_vulnerability_report(vulnerabilities_found)

def get_severity(vuln_type: str) -> str:
    """Determine severity level for vulnerability type"""
    severity_map = {
        "reentrancy": "HIGH",
        "integer_overflow": "MEDIUM", 
        "access_control": "HIGH",
        "unchecked_calls": "MEDIUM",
        "front_running": "MEDIUM"
    }
    return severity_map.get(vuln_type, "LOW")

def format_vulnerability_report(vulnerabilities: list) -> str:
    """Format the vulnerability analysis report"""
    if not vulnerabilities:
        return "✅ No obvious vulnerability patterns detected in the provided code."
    
    report = "🚨 VULNERABILITY ANALYSIS REPORT\n\n"
    
    for vuln in vulnerabilities:
        report += f"⚠️  {vuln['type'].upper()} VULNERABILITY\n"
        report += f"   Severity: {vuln['severity']}\n"
        report += f"   Pattern: {vuln['pattern']}\n"
        report += f"   Recommendation: {get_recommendation(vuln['type'])}\n\n"
    
    return report

def get_recommendation(vuln_type: str) -> str:
    """Get specific recommendation for vulnerability type"""
    recommendations = {
        "reentrancy": "Use checks-effects-interactions pattern and reentrancy guards",
        "integer_overflow": "Use SafeMath library or Solidity 0.8+ built-in overflow protection",
        "access_control": "Implement proper access control modifiers and role-based permissions",
        "unchecked_calls": "Always check return values of external calls",
        "front_running": "Use commit-reveal schemes or private mempools"
    }
    return recommendations.get(vuln_type, "Review code for security best practices")

def analyze_code_quality(code: str) -> str:
    """Analyze code for quality and optimization opportunities"""
    quality_issues = []
    optimizations = []
    
    code_lower = code.lower()
    
    # Check for gas optimization opportunities
    if "storage" in code_lower and "memory" in code_lower:
        optimizations.append("Consider using memory instead of storage for temporary variables")
    
    if "for (" in code_lower or "while (" in code_lower:
        quality_issues.append("Review loops for gas optimization opportunities")
    
    if "public" in code_lower:
        optimizations.append("Consider making functions external if they don't need internal access")
    
    if "uint256" in code_lower:
        optimizations.append("Consider using smaller uint sizes (uint8, uint16) where appropriate")
    
    # Check for readability issues
    if len(code.split('\n')) > 100:
        quality_issues.append("Consider breaking large functions into smaller, more manageable pieces")
    
    if "//" not in code and "/*" not in code:
        quality_issues.append("Add comments to explain complex logic")
    
    return format_quality_report(quality_issues, optimizations)

def format_quality_report(issues: list, optimizations: list) -> str:
    """Format the code quality analysis report"""
    report = "📋 CODE QUALITY ANALYSIS REPORT\n\n"
    
    if issues:
        report += "⚠️  IMPROVEMENTS NEEDED:\n"
        for issue in issues:
            report += f"   • {issue}\n"
        report += "\n"
    
    if optimizations:
        report += "⚡ OPTIMIZATION OPPORTUNITIES:\n"
        for opt in optimizations:
            report += f"   • {opt}\n"
        report += "\n"
    
    if not issues and not optimizations:
        report += "✅ Code quality looks good! No major issues detected.\n\n"
    
    return report

def is_smart_contract_code(text: str) -> bool:
    """Check if the input looks like smart contract code"""
    smart_contract_indicators = [
        "contract", "function", "modifier", "require", "assert",
        "mapping", "address", "uint", "bytes", "string",
        "pragma", "import", "library", "interface", "struct",
        "event", "emit", "payable", "view", "pure",
        "public", "private", "internal", "external"
    ]
    
    text_lower = text.lower()
    matches = sum(1 for indicator in smart_contract_indicators if indicator in text_lower)
    
    # If we find 3 or more smart contract keywords, likely it's smart contract code
    return matches >= 3

async def perform_comprehensive_analysis(ctx: Context, code: str) -> str:
    """Perform comprehensive security analysis"""
    
    try:
        # Perform traditional vulnerability analysis
        vuln_analysis = analyze_vulnerabilities(code)
        
        # Perform code quality analysis  
        quality_analysis = analyze_code_quality(code)
        
        # Generate AI-powered detailed analysis
        ai_analysis = await generate_ai_analysis(code, vuln_analysis, quality_analysis)
        
        # Format comprehensive report
        report = f"""🛡️ COMPREHENSIVE SECURITY ANALYSIS REPORT

═══════════════════════════════════════════════════════════════

🔍 VULNERABILITY ANALYSIS:
{vuln_analysis}

═══════════════════════════════════════════════════════════════

📝 CODE QUALITY REVIEW:
{quality_analysis}

═══════════════════════════════════════════════════════════════

🤖 DETAILED AI ANALYSIS:
{ai_analysis}

═══════════════════════════════════════════════════════════════

💡 RECOMMENDATIONS:
1. Address any HIGH severity vulnerabilities immediately
2. Implement suggested gas optimizations
3. Add comprehensive test coverage
4. Consider formal verification for critical functions
5. Implement proper access controls and error handling

This analysis was performed by the Security Analyzer Agent 🤖"""

        return report
        
    except Exception as e:
        ctx.logger.exception('Error during comprehensive analysis')
        return f"Error during comprehensive analysis: {str(e)}"

async def generate_ai_analysis(code: str, vuln_analysis: str, quality_analysis: str) -> str:
    """Generate AI-powered detailed analysis"""
    
    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": f"""
        You are an expert smart contract security auditor specializing in {subject_matter}.
        
        When analyzing code, provide:
        1. SECURITY ASSESSMENT: Overall risk level (LOW/MEDIUM/HIGH) based on all evidence
        2. VULNERABILITIES FOUND: List specific issues with detailed explanations
        3. EXPLOITATION SCENARIOS: How each vulnerability could be exploited
        4. REMEDIATION STEPS: Specific code changes needed to fix issues
        5. BEST PRACTICES: General security recommendations
        
        Focus on common vulnerabilities like:
        - Reentrancy attacks
        - Integer overflow/underflow
        - Access control bypass
        - Unchecked external calls
        - Front-running vulnerabilities
        - Flash loan attacks
        - Sandwich attacks
        
        Provide actionable, specific recommendations.
                """},
                {"role": "user", "content": f"""
        Code to Analyze:
        {code}
        
        Vulnerability Analysis:
        {vuln_analysis}
        
        Code Quality Analysis:
        {quality_analysis}
        
        Please provide a detailed security analysis of this smart contract code.
                """},
            ],
            max_tokens=2048,
        )

        return str(r.choices[0].message.content)
        
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

    # Check if this looks like smart contract code
    if not is_smart_contract_code(text):
        response = """🤖 I'm a Smart Contract Security Analyzer specializing in comprehensive security analysis!

I can provide:
• 🔍 Advanced Vulnerability Detection Analysis
• 📝 Code Quality Review
• ⚡ Gas Optimization Recommendations
• 🛡️ Security Best Practices Assessment
• 🎯 Intelligent Risk Assessment
• 🧠 Evidence-based Analysis

Please send me smart contract code (Solidity, JavaScript, or other dApp code) for comprehensive security analysis!

Example vulnerabilities I can detect:
• Reentrancy attacks
• Integer overflow/underflow
• Access control bypasses
• Unchecked external calls
• Front-running vulnerabilities
• Flash loan attacks
• Sandwich attacks"""
    else:
        # Perform comprehensive analysis
        response = await perform_comprehensive_analysis(ctx, text)
    
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
