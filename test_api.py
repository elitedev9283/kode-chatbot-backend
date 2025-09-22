"""
Simple test script to demonstrate the chatbot API functionality.
Run this after starting the server to test the endpoints.
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_root():
    """Test the root endpoint."""
    print("🔍 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_chat():
    """Test the chat functionality."""
    print("🔍 Testing chat endpoint...")
    
    # Test message without OpenAI key (should show error handling)
    chat_data = {
        "message": "Hello, how are you?",
        "conversation_id": None
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/",
            headers={"Content-Type": "application/json"},
            json=chat_data
        )
        print(f"Chat Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Chat Response: {response.json()}")
        else:
            print(f"Chat Error: {response.json()}")
    except Exception as e:
        print(f"Chat request failed: {e}")
    print()

def test_conversation_management():
    """Test conversation management endpoints."""
    print("🔍 Testing conversation management...")
    
    # Create a new conversation
    try:
        response = requests.post(f"{BASE_URL}/api/v1/chat/conversation")
        print(f"Create Conversation Status: {response.status_code}")
        if response.status_code == 201:
            print(f"New Conversation: {response.json()}")
        else:
            print(f"Create Conversation Error: {response.json()}")
    except Exception as e:
        print(f"Create conversation failed: {e}")
    
    # List conversations
    try:
        response = requests.get(f"{BASE_URL}/api/v1/chat/conversations")
        print(f"List Conversations Status: {response.status_code}")
        print(f"Conversations: {response.json()}")
    except Exception as e:
        print(f"List conversations failed: {e}")
    print()

def main():
    """Run all tests."""
    print("🚀 Starting API Tests...\n")
    
    try:
        test_health()
        test_root()
        test_conversation_management()
        test_chat()
        
        print("✅ All basic tests completed!")
        print("\n📚 Next steps:")
        print("1. Add your OpenAI API key to .env file")
        print("2. Restart the server")
        print("3. Test chat functionality with a real API key")
        print("4. Visit http://localhost:8000/docs for interactive API documentation")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Start it with: python run.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()