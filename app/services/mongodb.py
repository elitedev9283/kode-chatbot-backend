"""
MongoDB service for chat history persistence.
"""
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.models.chat import ConversationHistory, ChatMessage


class MongoDBService:
    """MongoDB service for managing chat conversations."""
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.database = self.client[settings.mongodb_database]
            self.collection = self.database[settings.mongodb_collection]
            
        except Exception as e:
            print(f"Warning: Failed to connect to MongoDB: {e}")
            self.client = None
            self.database = None
            self.collection = None
    
    async def _test_connection(self):
        """Test MongoDB connection."""
        try:
            if self.client:
                await self.client.admin.command('ping')
                print("MongoDB connection successful")
        except Exception as e:
            print(f"MongoDB connection test failed: {e}")
    
    async def save_conversation(self, conversation: ConversationHistory) -> bool:
        """
        Save or update a conversation in MongoDB.
        
        Args:
            conversation: ConversationHistory object to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.collection is None:
            return False
        
        try:
            # Convert to dict for MongoDB storage
            conversation_dict = conversation.model_dump()
            conversation_dict["updated_at"] = datetime.now(timezone.utc)
            
            # Use upsert to create or update
            result = await self.collection.update_one(
                {"conversation_id": conversation.conversation_id},
                {"$set": conversation_dict},
                upsert=True
            )
            return result.acknowledged
            
        except PyMongoError as e:
            print(f"Error saving conversation to MongoDB: {e}")
            return False
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationHistory]:
        """
        Retrieve a conversation from MongoDB.
        
        Args:
            conversation_id: The conversation ID to retrieve
            
        Returns:
            ConversationHistory object or None if not found
        """
        if self.collection is None:
            return None
        
        try:
            doc = await self.collection.find_one({"conversation_id": conversation_id})
            if doc:
                # Convert MongoDB document back to ConversationHistory
                # Handle timestamp conversion
                if "created_at" in doc and isinstance(doc["created_at"], str):
                    doc["created_at"] = datetime.fromisoformat(doc["created_at"].replace('Z', '+00:00'))
                if "updated_at" in doc and isinstance(doc["updated_at"], str):
                    doc["updated_at"] = datetime.fromisoformat(doc["updated_at"].replace('Z', '+00:00'))
                
                # Convert message timestamps
                for msg in doc.get("messages", []):
                    if "timestamp" in msg and isinstance(msg["timestamp"], str):
                        msg["timestamp"] = datetime.fromisoformat(msg["timestamp"].replace('Z', '+00:00'))
                
                return ConversationHistory(**doc)
            return None
            
        except PyMongoError as e:
            print(f"Error retrieving conversation from MongoDB: {e}")
            return None
    
    async def list_conversations(self) -> List[Dict[str, Any]]:
        """
        List all conversations from MongoDB.
        
        Returns:
            List of conversation summaries
        """
        if self.collection is None:
            return []
        
        try:
            cursor = self.collection.find({}, {
                "conversation_id": 1,
                "messages": 1,
                "created_at": 1,
                "updated_at": 1
            }).sort("updated_at", -1)
            
            conversations = []
            async for doc in cursor:
                # Handle timestamp conversion
                if "created_at" in doc and isinstance(doc["created_at"], str):
                    doc["created_at"] = datetime.fromisoformat(doc["created_at"].replace('Z', '+00:00'))
                if "updated_at" in doc and isinstance(doc["updated_at"], str):
                    doc["updated_at"] = datetime.fromisoformat(doc["updated_at"].replace('Z', '+00:00'))
                
                conversation_summary = {
                    "conversation_id": doc["conversation_id"],
                    "message_count": len(doc.get("messages", [])),
                    "created_at": doc["created_at"].isoformat() if doc.get("created_at") else None,
                    "updated_at": doc["updated_at"].isoformat() if doc.get("updated_at") else None,
                    "last_message": doc["messages"][-1]["content"][:50] + "..." if doc.get("messages") else ""
                }
                conversations.append(conversation_summary)
            
            return conversations
            
        except PyMongoError as e:
            print(f"Error listing conversations from MongoDB: {e}")
            return []
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation from MongoDB.
        
        Args:
            conversation_id: The conversation ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.collection is None:
            return False
        
        try:
            result = await self.collection.delete_one({"conversation_id": conversation_id})
            return result.deleted_count > 0
            
        except PyMongoError as e:
            print(f"Error deleting conversation from MongoDB: {e}")
            return False
    
    async def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()


# Global MongoDB service instance
mongodb_service = MongoDBService()
