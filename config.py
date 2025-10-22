import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # GitHub Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    # Hedera Configuration
    HEDERA_OPERATOR_ID = os.getenv("HEDERA_OPERATOR_ID")
    HEDERA_OPERATOR_KEY = os.getenv("HEDERA_OPERATOR_KEY")
    HEDERA_TOPIC_ID = os.getenv("HEDERA_TOPIC_ID", "default_topic")
    
    # ASI Configuration
    ASI_API_KEY = os.getenv("ASI_API_KEY")
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # API Configuration
    GITHUB_API_BASE = "https://api.github.com"
    ASI_API_BASE = "https://api.asi1.ai/v1"
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        missing = []
        
        if not cls.GITHUB_TOKEN:
            missing.append("GITHUB_TOKEN")
        
        if not cls.HEDERA_OPERATOR_ID:
            missing.append("HEDERA_OPERATOR_ID")
            
        if not cls.HEDERA_OPERATOR_KEY:
            missing.append("HEDERA_OPERATOR_KEY")
        
        if missing:
            print(f"Warning: Missing configuration: {', '.join(missing)}")
            print("Some features may not work properly.")
        
        return len(missing) == 0
