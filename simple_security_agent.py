from datetime import datetime
from uuid import uuid4
import asyncio
import re
import json
import shutil
import subprocess
import tempfile

import os

from openai import OpenAI
from uagents import Context, Protocol, Agent, Model
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    TextContent,
    chat_protocol_spec,
)

### Comprehensive Security Analysis Agent with MeTTa integration

# the subject that this assistant is an expert in
subject_matter = "comprehensive smart contract security analysis and vulnerability detection"

# ASI client - replace '<your_api_key>' with your key in deployment
client = OpenAI(
    base_url='https://api.asi1.ai/v1',
    api_key='sk_ef5bd03613464e6e8af79d8aa362a1a3f3d8145f5e314bf3af40a37aff301dca',
)

agent = Agent(
    name="security_analyzer",
    seed="security_analyzer_unique_seed_2024"
)

# We create a new protocol which is compatible with the chat protocol spec
protocol = Protocol(spec=chat_protocol_spec)

# -------------------------
# Existing vulnerability/quality analyzers (unchanged)
# -------------------------
VULNERABILITY_PATTERNS = {
    "reentrancy": [
        "external call before state change",
        "msg.sender.call()",
        "delegatecall",
        "state variable not updated before external call"
    ],
    "integer_overflow": [
        "unchecked arithmetic",
        "safemath not used",
        "uint256 overflow",
        "unchecked add/sub/mul"
    ],
    "access_control": [
        "missing onlyowner modifier",
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
        "mev vulnerability",
        "transaction ordering dependency"
    ]
}

def analyze_vulnerabilities(code: str) -> list:
    """Analyze code for common vulnerability patterns - returns list of findings (dicts)"""
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
    return vulnerabilities_found

def get_severity(vuln_type: str) -> str:
    severity_map = {
        "reentrancy": "HIGH",
        "integer_overflow": "MEDIUM",
        "access_control": "HIGH",
        "unchecked_calls": "MEDIUM",
        "front_running": "MEDIUM"
    }
    return severity_map.get(vuln_type, "LOW")

def format_vulnerability_report_list(vulnerabilities: list) -> str:
    """Format the vulnerability analysis report from a list of findings"""
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
    recommendations = {
        "reentrancy": "Use checks-effects-interactions pattern and reentrancy guards (e.g., OpenZeppelin ReentrancyGuard).",
        "integer_overflow": "Use SafeMath library or Solidity 0.8+ built-in overflow protection.",
        "access_control": "Implement proper access control modifiers and role-based permissions (use multisig for admin).",
        "unchecked_calls": "Always check return values of external calls and consider using .call with gas limits carefully.",
        "front_running": "Use commit-reveal schemes, or private txs / off-chain ordering to mitigate front-running."
    }
    return recommendations.get(vuln_type, "Review code for security best practices")

def analyze_code_quality(code: str) -> dict:
    """Analyze code for quality and optimization opportunities; return dict"""
    quality_issues = []
    optimizations = []
    code_lower = code.lower()
    # Gas optimization hints
    if "storage" in code_lower and "memory" in code_lower:
        optimizations.append("Consider using memory instead of storage for temporary variables when appropriate.")
    if "for (" in code_lower or "while (" in code_lower:
        quality_issues.append("Review loops for gas optimization opportunities (avoid unbounded loops).")
    if "public" in code_lower:
        optimizations.append("Consider making functions external if they don't need internal access.")
    if "uint256" in code_lower:
        optimizations.append("Consider using tighter integer sizes (uint8, uint16) for storage where safe.")
    if len(code.split('\n')) > 300:
        quality_issues.append("Consider breaking large files/functions into smaller modules for maintainability.")
    if "//" not in code_lower and "/*" not in code_lower:
        quality_issues.append("Add comments and NatSpec to explain complex logic and invariants.")
    return {"issues": quality_issues, "optimizations": optimizations}

def format_quality_report_dict(quality: dict) -> str:
    report = "📋 CODE QUALITY ANALYSIS REPORT\n\n"
    issues = quality.get("issues", [])
    optimizations = quality.get("optimizations", [])
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
    smart_contract_indicators = [
        "contract", "function", "modifier", "require", "assert",
        "mapping", "address", "uint", "bytes", "string",
        "pragma", "import", "library", "interface", "struct",
        "event", "emit", "payable", "view", "pure",
        "public", "private", "internal", "external"
    ]
    text_lower = text.lower()
    matches = sum(1 for indicator in smart_contract_indicators if indicator in text_lower)
    return matches >= 3

# Removed MeTTa integration for simplicity

# -------------------------
# AI prompt builder
# -------------------------
async def generate_ai_analysis(code: str, vuln_analysis: list, quality_analysis: dict) -> str:
    """
    Provide the ASI model with the code + local analyses
    so it can produce a detailed, evidence-backed AI analysis.
    """
    vuln_text = format_vulnerability_report_list(vuln_analysis)
    quality_text = format_quality_report_dict(quality_analysis)

    prompt_system = f"""
You are an expert smart contract security auditor specializing in {subject_matter}.
Use the provided local vulnerability and code-quality analyses to produce a clear, actionable security analysis.

Reply with:
1) SECURITY ASSESSMENT: Overall risk level (LOW/MEDIUM/HIGH)
2) VULNERABILITIES FOUND: List specific issues, referencing the local findings
3) EXPLOITATION SCENARIOS: Short explanation for how issues could be exploited
4) REMEDIATION STEPS: Specific code actions to fix issues
5) BEST PRACTICES: High-level recommendations

Be concise and actionable. Do NOT provide internal chain-of-thought.
"""

    user_message = f"""
Code to Analyze:
{code}

Vulnerability Findings:
{vuln_text}

Code Quality Findings:
{quality_text}

Provide a detailed, specific security analysis referencing above items.
"""

    try:
        r = client.chat.completions.create(
            model="asi1-mini",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": user_message},
            ],
            max_tokens=2048,
        )
        return str(r.choices[0].message.content)
    except Exception as e:
        return f"Unable to generate AI analysis: {str(e)}"

# -------------------------
# Orchestrator: run full analysis (local -> AI)
# -------------------------
async def perform_comprehensive_analysis(ctx: Context, code: str) -> str:
    try:
        vuln_list = analyze_vulnerabilities(code)
        quality = analyze_code_quality(code)

        # Call ASI with the data
        ai_analysis = await generate_ai_analysis(code, vuln_list, quality)

        # Build combined comprehensive report
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "vulnerability_findings": vuln_list,
            "vulnerability_text": format_vulnerability_report_list(vuln_list),
            "quality_findings": quality,
            "quality_text": format_quality_report_dict(quality),
            "ai_analysis": ai_analysis
        }

        # Optionally persist to reports directory
        try:
            os.makedirs("reports", exist_ok=True)
            fname = f"reports/report_{int(datetime.utcnow().timestamp())}.json"
            with open(fname, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            ctx.logger.info(f"Saved report -> {fname}")
        except Exception:
            ctx.logger.exception("Failed to save report file")

        # Format human-friendly summary to return to user (keep it concise)
        summary_lines = [
            "🛡️ COMPREHENSIVE SECURITY ANALYSIS REPORT",
            f"Vulnerabilities detected: {len(vuln_list)}",
            f"Code quality issues: {len(quality.get('issues',[]))}",
            "",
            "📋 DETAILED AI ANALYSIS:",
            ai_analysis
        ]
        return "\n\n".join(summary_lines)

    except Exception as e:
        ctx.logger.exception('Error during comprehensive analysis')
        return f"Error during comprehensive analysis: {str(e)}"


# -------------------------
# Chat handler (preserve your original flow)
# -------------------------
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
        response = """🤖 I'm a Smart Contract Security Analyzer specializing in comprehensive security analysis.

I can provide:
• 🔍 Vulnerability Detection Analysis
• 📝 Code Quality Review
• ⚡ Gas Optimization Recommendations
• 🛡️ Security Best Practices Assessment
• 🎯 Overall Risk Assessment

Please send me smart contract code (Solidity, JavaScript, or other dApp code) for comprehensive security analysis!

Example vulnerabilities I can detect:
• Reentrancy attacks
• Integer overflow/underflow
• Access control bypasses
• Unchecked external calls
• Front-running vulnerabilities"""
    else:
        # Perform comprehensive analysis (local -> AI)
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
    # we are not interested in the acknowledgements for this example
    pass

# attach the protocol to the agent
agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
