"""
Startup check script to verify MongoDB connectivity.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))


async def check_mongodb():
    """Check MongoDB connectivity."""
    try:
        from app.services.mongodb import mongodb_service
        
        print("🔍 Checking MongoDB connectivity...")
        await mongodb_service._test_connection()
        print("✅ MongoDB connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure MongoDB is running")
        print("2. Check MONGODB_URI in your .env file")
        print("3. Verify network connectivity")
        print("4. Check MongoDB authentication if using cloud instance")
        return False


async def check_openai():
    """Check OpenAI configuration."""
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("✅ OpenAI API key configured")
        return True
    else:
        print("❌ OpenAI API key not configured")
        print("💡 Add OPENAI_API_KEY to your .env file")
        return False


async def main():
    """Run all startup checks."""
    print("🚀 Chatbot Backend Startup Check")
    print("=" * 40)
    
    # Check MongoDB
    mongodb_ok = await check_mongodb()
    
    # Check OpenAI
    openai_ok = await check_openai()
    
    print("\n" + "=" * 40)
    
    if mongodb_ok and openai_ok:
        print("🎉 All checks passed! You can start the application.")
        print("💡 Run: python run.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues before starting.")
        if not mongodb_ok:
            print("   - MongoDB connection required for chat history persistence")
        if not openai_ok:
            print("   - OpenAI API key required for chatbot functionality")
    
    # Close MongoDB connection
    try:
        from app.services.mongodb import mongodb_service
        await mongodb_service.close()
    except:
        pass


if __name__ == "__main__":
    asyncio.run(main())
