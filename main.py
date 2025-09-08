# main.py
import asyncio
import json
from core.orchestrator import AIOrchestrator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def load_config():
    """Load configuration from environment variables and config files"""
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "twitter_api_key": os.getenv("TWITTER_API_KEY"),
        "twitter_api_secret": os.getenv("TWITTER_API_SECRET"),
        "twitter_access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
        "twitter_access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "facebook_app_id": os.getenv("FACEBOOK_APP_ID"),
        "facebook_app_secret": os.getenv("FACEBOOK_APP_SECRET"),
        "facebook_access_token": os.getenv("FACEBOOK_ACCESS_TOKEN"),
        "facebook_page_id": os.getenv("FACEBOOK_PAGE_ID"),
        "stripe_secret_key": os.getenv("STRIPE_SECRET_KEY"),
        "stripe_public_key": os.getenv("STRIPE_PUBLIC_KEY"),
        "owner_account": os.getenv("OWNER_ACCOUNT"),
        "ai_fund_account": os.getenv("AI_FUND_ACCOUNT"),
        "reserve_account": os.getenv("RESERVE_ACCOUNT"),
        "security_level": os.getenv("SECURITY_LEVEL", "military")
    }

async def main():
    """Main application entry point"""
    print("Starting AEGIS Synthetic Intelligence System...")
    
    # Load configuration
    config = load_config()
    
    # Initialize the AI orchestrator
    orchestrator = AIOrchestrator()
    
    # Deploy AI agents
    agents_config = {
        "content_creator": {"openai_api_key": config["openai_api_key"]},
        "social_poster": {
            "twitter_api_key": config["twitter_api_key"],
            "twitter_api_secret": config["twitter_api_secret"],
            "twitter_access_token": config["twitter_access_token"],
            "twitter_access_token_secret": config["twitter_access_token_secret"],
            "facebook_app_id": config["facebook_app_id"],
            "facebook_app_secret": config["facebook_app_secret"],
            "facebook_access_token": config["facebook_access_token"],
            "facebook_page_id": config["facebook_page_id"]
        },
        "payment_processor": {
            "stripe_secret_key": config["stripe_secret_key"],
            "owner_account": config["owner_account"],
            "ai_fund_account": config["ai_fund_account"],
            "reserve_account": config["reserve_account"]
        },
        "security_monitor": {
            "security_level": config["security_level"]
        }
    }
    
    # Deploy all agents
    for agent_type, agent_config in agents_config.items():
        await orchestrator.deploy_agent(agent_type, agent_config)
    
    print(f"Deployed {len(orchestrator.agents)} AI agents")
    
    # Start the orchestrator
    try:
        await orchestrator.run()
    except KeyboardInterrupt:
        print("Shutting down AEGIS system...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print("AEGIS system shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
