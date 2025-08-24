# Chatbot Backend (FastAPI + LangGraph + MongoDB)

A modern chatbot backend built with FastAPI and LangGraph, featuring conversation management, OpenAI integration, and MongoDB persistence for chat history.

## 🏗️ Architecture

```
kode-chatbot-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── chat.py          # Chat data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chatbot.py       # LangGraph chatbot service
│   │   └── mongodb.py       # MongoDB service for persistence
│   └── api/
│       ├── __init__.py
│       └── chat.py          # Chat API endpoints
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables example
├── test_mongodb.py         # MongoDB integration test script
└── run.py                  # Simple startup script
```

## 🚀 Features

- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **LangGraph Integration**: Sophisticated conversation flow management
- **OpenAI Integration**: GPT-powered responses
- **MongoDB Persistence**: Persistent chat history storage
- **Conversation Management**: Full CRUD operations for conversations
- **RESTful API**: Clean, well-documented endpoints
- **CORS Support**: Frontend integration ready
- **Health Checks**: System monitoring endpoints
- **Async Operations**: High-performance async database operations

## 📋 Prerequisites

- Python 3.12+
- OpenAI API Key
- MongoDB instance (local or cloud)

## 🛠️ Installation & Setup

### 1. Clone and Navigate
```bash
cd kode-chatbot-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Configuration
1. Copy the example environment file:
   ```bash
   copy env.example .env    # Windows
   cp env.example .env      # Linux/Mac
   ```

2. Edit `.env` and add your configuration:
   ```env
   # OpenAI Configuration
   OPENAI_API_KEY=your_actual_openai_api_key_here
   
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE=kode_chatbot
   MONGODB_COLLECTION=conversations
   
   # Server Configuration
   DEBUG=false
   HOST=0.0.0.0
   PORT=8000
   ```

### 6. MongoDB Setup

**Option A: Local MongoDB**
```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data/db
```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Get connection string and update `MONGODB_URI` in `.env`

### 7. Run the Application

**Option 1: Using the run script**
```bash
python run.py
```

**Option 2: Using uvicorn directly**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 3: Using Python module**
```bash
python -m app.main
```

## 📚 API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔗 API Endpoints

### Core Endpoints
- `GET /` - Welcome message and API info
- `GET /health` - Health check and configuration status

### Chat Endpoints
- `POST /api/v1/chat/` - Send a message to the chatbot
- `POST /api/v1/chat/conversation` - Create a new conversation
- `GET /api/v1/chat/conversation/{id}/history` - Get conversation history
- `GET /api/v1/chat/conversations` - List all conversations
- `DELETE /api/v1/chat/conversation/{id}` - Delete a conversation

### Example Usage

**Start a conversation:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, how are you?",
       "conversation_id": null
     }'
```

**Continue conversation:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Tell me a joke",
       "conversation_id": "your-conversation-id-here"
     }'
```

**Get conversation history:**
```bash
curl "http://localhost:8000/api/v1/chat/conversation/your-conversation-id-here/history"
```

**List all conversations:**
```bash
curl "http://localhost:8000/api/v1/chat/conversations"
```

**Delete a conversation:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/chat/conversation/your-conversation-id-here"
```

## ⚙️ Configuration

Key configuration options in `app/core/config.py`:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-3.5-turbo)
- `MONGODB_URI`: MongoDB connection string (default: mongodb://localhost:27017)
- `MONGODB_DATABASE`: Database name (default: kode_chatbot)
- `MONGODB_COLLECTION`: Collection name (default: conversations)
- `DEBUG`: Enable debug mode (default: False)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## 🧪 Testing

**Test MongoDB integration:**
```bash
python test_mongodb.py
```

**Test application import:**
```bash
python -c "from app.main import app; print('✅ App imports successfully!')"
```

**Check health endpoint:**
```bash
curl http://localhost:8000/health
```

## 🏗️ Project Structure Details

### `/app/core/`
- Configuration management and application settings

### `/app/models/`
- Pydantic models for request/response validation
- Data structures for chat messages and conversations

### `/app/services/`
- Business logic and LangGraph integration
- Chatbot service with conversation management
- MongoDB service for data persistence

### `/app/api/`
- FastAPI route handlers
- API endpoint definitions

## 🗄️ MongoDB Integration

The application now uses MongoDB for persistent storage of chat conversations:

- **Automatic Persistence**: All conversations are automatically saved to MongoDB
- **Conversation History**: Full message history is preserved across sessions
- **Scalable Storage**: MongoDB handles large volumes of conversations efficiently
- **Async Operations**: Non-blocking database operations for better performance

### MongoDB Collections

- **conversations**: Stores conversation metadata and message history
- **Indexes**: Automatic indexing on `conversation_id` for fast lookups

## 🚨 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your `.env` file contains a valid `OPENAI_API_KEY`
   - Check that the API key has sufficient credits

2. **MongoDB Connection Error**
   - Verify MongoDB is running and accessible
   - Check `MONGODB_URI` in your `.env` file
   - Ensure network connectivity to MongoDB instance

3. **Import Errors**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed: `pip install -r requirements.txt`

4. **Port Already in Use**
   - Change the port in `.env` file or kill the process using port 8000

### Getting Help

1. Check the logs when starting the application
2. Visit `/health` endpoint to verify configuration
3. Use `/docs` for interactive API testing
4. Run `python test_mongodb.py` to test database connectivity

## 🔮 Next Steps

- Add user authentication and authorization
- Implement conversation search and filtering
- Add rate limiting and API quotas
- Implement streaming responses
- Add conversation analytics and metrics
- Integration with different LLM providers
- Add conversation export/import functionality

## 📝 License

This project is open source and available under the MIT License.
