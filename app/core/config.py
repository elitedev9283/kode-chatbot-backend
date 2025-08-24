"""
Configuration settings for the chatbot application.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_title: str = "Chatbot API"
    api_description: str = "FastAPI + LangGraph Chatbot Backend"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-3.5-turbo"
    
    # Pinecone Configuration
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "koda-knowledge")
    pinecone_name_space: str = os.getenv("PINECONE_NAME_SPACE", "kodekloud")

    # MCP Server Configuration
    mcp_server_url: str = os.getenv("MCP_SERVER_URL", "http://localhost:3001")
    
    # MongoDB Configuration
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "kode_chatbot")
    mongodb_collection: str = os.getenv("MONGODB_COLLECTION", "conversations")

    # CORS Configuration
    allowed_origins: list[str] = ["http://localhost:3000"]
    allowed_credentials: bool = True
    allowed_methods: list[str] = ["*"]
    allowed_headers: list[str] = ["*"]
    
    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()