import os
import json
from typing import Dict, Any, Optional

def submit_proof(topic_id: str, message: Dict[str, Any]) -> str:
    """Submit proof to Hedera Consensus Service"""
    try:
        # Try to import Hedera SDK
        try:
            from hedera import Client, TopicMessageSubmitTransaction, TopicId
        except ImportError:
            print("Hedera SDK not installed. Using mock transaction ID.")
            return f"mock_tx_{hash(str(message))}"
        
        # Initialize Hedera client
        client = Client.for_testnet()
        
        # Set operator credentials
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        operator_key = os.getenv("HEDERA_OPERATOR_KEY")
        
        if not operator_id or not operator_key:
            print("Hedera credentials not found. Using mock transaction ID.")
            return f"mock_tx_{hash(str(message))}"
        
        client.setOperator(operator_id, operator_key)
        
        # Create and execute transaction
        tx = (TopicMessageSubmitTransaction()
              .setTopicId(TopicId.fromString(topic_id))
              .setMessage(json.dumps(message))
              .execute(client))
        
        receipt = tx.getReceipt(client)
        return str(receipt.transactionId)
        
    except Exception as e:
        print(f"Hedera submission failed: {str(e)}")
        # Return mock transaction ID on failure
        return f"mock_tx_{hash(str(message))}"

def create_consensus_topic(memo: str = "ProofForge Evaluation Topic") -> Optional[str]:
    """Create a new Hedera Consensus Topic"""
    try:
        # Try to import Hedera SDK
        try:
            from hedera import Client, TopicCreateTransaction
        except ImportError:
            print("Hedera SDK not installed. Cannot create topic.")
            return None
        
        # Initialize Hedera client
        client = Client.for_testnet()
        
        # Set operator credentials
        operator_id = os.getenv("HEDERA_OPERATOR_ID")
        operator_key = os.getenv("HEDERA_OPERATOR_KEY")
        
        if not operator_id or not operator_key:
            print("Hedera credentials not found. Cannot create topic.")
            return None
        
        client.setOperator(operator_id, operator_key)
        
        # Create topic transaction
        tx = TopicCreateTransaction().setTopicMemo(memo).execute(client)
        
        receipt = tx.getReceipt(client)
        topic_id = str(receipt.topicId)
        
        print(f"Created Hedera topic: {topic_id}")
        return topic_id
        
    except Exception as e:
        print(f"Failed to create Hedera topic: {str(e)}")
        return None

def get_hedera_explorer_url(transaction_id: str) -> str:
    """Generate Hedera testnet explorer URL for a transaction"""
    if transaction_id.startswith("mock_tx_"):
        return "https://hashscan.io/testnet (mock transaction)"
    
    # Convert transaction ID format if needed
    tx_id = transaction_id.replace("-", "@")
    return f"https://hashscan.io/testnet/transaction/{tx_id}"
