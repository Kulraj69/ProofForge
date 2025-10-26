# 🧠 ProofForge: Explainable AI Meets Hedera

**Agents that reason and prove** - A revolutionary platform where explainable AI meets blockchain verification, creating transparent, auditable, and trustworthy code evaluation systems anchored on Hedera.

## 🚀 What is ProofForge?

ProofForge is a cutting-edge platform that combines the power of explainable AI with blockchain immutability to create the world's first **reasoning and proving agents** for code evaluation. Our agents don't just analyze code—they think, reason, and provide verifiable proofs of their analysis anchored on the Hedera blockchain.

## 🎯 Core Features

### 🧠 **Intelligent Agents**
- **Security Analyzer Agent**: Comprehensive smart contract security analysis with ASI integration
- **Repository Evaluator Agent**: Advanced code quality assessment and community engagement analysis
- **Reasoning Engine**: AI-powered analysis that explains its decisions step-by-step

### 🔗 **Blockchain Integration**
- **Hedera Consensus Service**: Immutable proof anchoring on enterprise-grade blockchain
- **IPFS Storage**: Decentralized storage for comprehensive analysis reports
- **Verifiable Proofs**: Every analysis is cryptographically verifiable and tamper-proof

### 📊 **Explainable AI**
- **Transparent Reasoning**: See exactly how our agents reach their conclusions
- **Detailed Traces**: Step-by-step analysis with evidence and recommendations
- **Auditable Results**: Every decision is backed by verifiable data and reasoning

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** - Modern Python for optimal performance
- **GitHub Token** (recommended) - Avoids rate limits and enables full API access
- **Hedera Testnet Account** - Get your operator ID and private key from [Hedera Portal](https://portal.hedera.com)
- **ASI API Key** (optional) - For advanced AI-powered analysis

### Installation
```bash
# Clone the repository
git clone https://github.com/Kulraj69/ProofForge.git
cd ProofForge

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the project root:
```bash
# GitHub API (recommended for full functionality)
GITHUB_TOKEN=ghp_your_github_token_here

# Hedera testnet credentials
HEDERA_OPERATOR_ID=0.0.123456
HEDERA_OPERATOR_KEY=your_private_key_here
HEDERA_TOPIC_ID=0.0.789012

# ASI API for advanced AI analysis (optional but powerful)
ASI_API_KEY=sk_your_asi_api_key_here
```

### Launch ProofForge
```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python main.py
```

🎉 **Access the platform**: Visit `http://localhost:8000/docs` for the interactive Swagger UI

## 🔌 API Endpoints

### 🎯 **POST /evaluate**
Evaluates a GitHub repository and submits proof to Hedera.

**Request:**
```json
{
  "repo_url": "https://github.com/owner/repo"
}
```

**Response:**
```json
{
  "repo": "owner/repo",
  "score": 45,
  "trace": ["has tests: +20", "stars > 100: +15", "active commits: +10"],
  "trace_hash": "abc123...",
  "hedera_tx": "0.0.123456@1640995200.123456789",
  "timestamp": "2023-12-01T12:00:00Z",
  "ipfs_hash": "QmXxXxXx...",
  "ipfs_url": "https://ipfs.io/ipfs/QmXxXxXx..."
}
```

### 📊 **GET /results/{owner}/{repo}**
Get all evaluation results for a specific repository.

### 📋 **GET /results**
Get all evaluation results across all repositories.

### 🔗 **POST /create_topic**
Create a new Hedera Consensus Topic for storing proofs.

### ⚡ **POST /submit_to_hedera**
Low-level helper: sends arbitrary JSON message to Hedera topic.

### 📈 **GET /metrics**
Get performance metrics and system health information.

## ⚙️ Configuration

### Environment Variables
Create a `.env` file with the following variables:

```bash
# GitHub API (recommended)
GITHUB_TOKEN=ghp_your_github_token_here

# Hedera testnet credentials
HEDERA_OPERATOR_ID=0.0.123456
HEDERA_OPERATOR_KEY=your_private_key_here
HEDERA_TOPIC_ID=0.0.789012

# ASI API for advanced AI analysis (optional)
ASI_API_KEY=sk_your_asi_api_key_here

# Optional settings
DEBUG=True
LOG_LEVEL=INFO
```

### 🔑 Getting Your Credentials

**GitHub Token:**
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `repo` scope
3. Copy the token to your `.env` file

**Hedera Testnet Account:**
1. Visit [Hedera Portal](https://portal.hedera.com)
2. Create a testnet account
3. Get your operator ID and private key
4. Create a Consensus Topic for storing proofs

**ASI API Key:**
1. Visit [ASI Dashboard](https://asi1.ai/dashboard/api-keys)
2. Create an account and generate an API key
3. Add the key to your `.env` file for enhanced AI analysis

## 🏗️ Architecture

### **Core Components**
- **🧠 AI Agents**: Security Analyzer and Repository Evaluator agents with ASI integration
- **🔗 Blockchain Layer**: Hedera Consensus Service for immutable proof anchoring
- **📊 Analysis Engine**: Explainable AI with step-by-step reasoning and evidence
- **💾 Storage**: Local JSON persistence with IPFS integration for decentralized storage
- **🌐 API Layer**: FastAPI with Swagger UI for seamless integration

### **Technology Stack**
- **Backend**: FastAPI with async/await for high performance
- **AI Integration**: ASI (Artificial Superintelligence Alliance) for advanced reasoning
- **Blockchain**: Hedera Consensus Service (enterprise-grade, carbon-negative)
- **Storage**: IPFS for decentralized, immutable proof storage
- **Monitoring**: Built-in performance metrics and health checks

## 🌟 Why ProofForge?

### **Revolutionary Approach**
- **First-of-its-kind**: The world's first reasoning and proving agents for code evaluation
- **Explainable AI**: Every decision is transparent and auditable
- **Blockchain Immutability**: All proofs are cryptographically verifiable and tamper-proof
- **Enterprise-Grade**: Built on Hedera's carbon-negative, enterprise-ready blockchain

### **Real-World Impact**
- **Developer Trust**: Build confidence in code quality with verifiable proofs
- **Audit Transparency**: Provide clear, evidence-based security assessments
- **Community Standards**: Establish new benchmarks for code evaluation
- **Future-Proof**: Scalable architecture ready for the next generation of AI agents

## 📄 License

Apache-2.0 License - Open source and ready for the community to build upon.

---

**🧠 ProofForge: Where AI meets blockchain to create the future of verifiable code evaluation.**