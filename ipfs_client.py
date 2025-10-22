import os
import json
from typing import Dict, Any, Optional

def upload_to_ipfs(data: Dict[str, Any]) -> Optional[str]:
    """Upload data to IPFS and return hash"""
    try:
        # Try to import IPFS client
        try:
            import ipfshttpclient
        except ImportError:
            print("IPFS client not installed. Using mock hash.")
            return f"mock_ipfs_{hash(str(data))}"
        
        # Connect to IPFS node
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
        
        # Convert data to JSON string
        json_data = json.dumps(data, indent=2)
        
        # Upload to IPFS
        result = client.add_str(json_data)
        ipfs_hash = result['Hash']
        
        print(f"Data uploaded to IPFS: {ipfs_hash}")
        return ipfs_hash
        
    except Exception as e:
        print(f"IPFS upload failed: {str(e)}")
        # Return mock hash on failure
        return f"mock_ipfs_{hash(str(data))}"

def get_from_ipfs(ipfs_hash: str) -> Optional[Dict[str, Any]]:
    """Retrieve data from IPFS using hash"""
    try:
        # Try to import IPFS client
        try:
            import ipfshttpclient
        except ImportError:
            print("IPFS client not installed. Cannot retrieve data.")
            return None
        
        # Connect to IPFS node
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
        
        # Get data from IPFS
        data = client.cat(ipfs_hash)
        json_data = json.loads(data.decode('utf-8'))
        
        return json_data
        
    except Exception as e:
        print(f"IPFS retrieval failed: {str(e)}")
        return None

def get_ipfs_url(ipfs_hash: str) -> str:
    """Get IPFS gateway URL for hash"""
    if ipfs_hash.startswith("mock_ipfs_"):
        return f"https://ipfs.io/ipfs/{ipfs_hash} (mock hash)"
    
    return f"https://ipfs.io/ipfs/{ipfs_hash}"
