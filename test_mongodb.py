"""
Test script for MongoDB integration.
"""
import asyncio
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.mongodb import mongodb_service
from app.models.chat import ConversationHistory, ChatMessage


async def test_mongodb():
    """Test MongoDB operations."""
    print("🧪 Testing MongoDB Integration...")
    
    # Test connection
    print("1. Testing connection...")
    try:
        await mongodb_service._test_connection()
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return
    
    # Test conversation creation
    print("\n2. Testing conversation creation...")
    conversation = ConversationHistory(
        conversation_id="test-conversation-123",
        messages=[
            ChatMessage(role="user", content="Hello, how are you?", timestamp=datetime.now(timezone.utc)),
            ChatMessage(role="assistant", content="I'm doing well, thank you!", timestamp=datetime.now(timezone.utc))
        ],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Save conversation
    saved = await mongodb_service.save_conversation(conversation)
    if saved:
        print("✅ Conversation saved successfully")
    else:
        print("❌ Failed to save conversation")
        return
    
    # Test conversation retrieval
    print("\n3. Testing conversation retrieval...")
    retrieved = await mongodb_service.get_conversation("test-conversation-123")
    if retrieved:
        print(f"✅ Conversation retrieved: {retrieved.conversation_id}")
        print(f"   Messages: {len(retrieved.messages)}")
    else:
        print("❌ Failed to retrieve conversation")
        return
    
    # Test listing conversations
    print("\n4. Testing conversation listing...")
    conversations = await mongodb_service.list_conversations()
    print(f"✅ Found {len(conversations)} conversations")
    for conv in conversations:
        print(f"   - {conv['conversation_id']}: {conv['message_count']} messages")
    
    # Test conversation deletion
    print("\n5. Testing conversation deletion...")
    deleted = await mongodb_service.delete_conversation("test-conversation-123")
    if deleted:
        print("✅ Conversation deleted successfully")
    else:
        print("❌ Failed to delete conversation")
    
    # Verify deletion
    retrieved_after_delete = await mongodb_service.get_conversation("test-conversation-123")
    if retrieved_after_delete is None:
        print("✅ Conversation successfully removed from database")
    else:
        print("❌ Conversation still exists after deletion")
    
    print("\n🎉 MongoDB integration test completed!")


if __name__ == "__main__":
    asyncio.run(test_mongodb())
