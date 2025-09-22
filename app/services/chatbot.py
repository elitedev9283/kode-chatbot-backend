"""
Chatbot service using LangGraph for conversation management.
"""
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
# from langchain_pinecone import PineconeVectorStore
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from app.core.config import settings
from app.models.chat import ChatMessage, ConversationHistory
from app.services.mongodb import mongodb_service
from pinecone import Pinecone
import requests
import loguru
logger = loguru.logger
# Initialize Pinecone
pc = Pinecone(api_key=settings.pinecone_api_key)
index = pc.Index(settings.pinecone_index_name)
print(index.describe_index_stats())

# Web search function
async def web_search(query: str) -> List[str]:
    return []
    """Perform a web search using the MCP server."""
    response = requests.get(f"{settings.mcp_server_url}/search", params={"query": query})
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


class ConversationState(TypedDict):
    """State structure for conversation graph.""" 
    messages: Annotated[List[BaseMessage], add_messages]
    conversation_id: str
    lesson: str


class ChatbotService:
    """Chatbot service managing conversations with LangGraph."""
    
    def __init__(self):
        """Initialize the chatbot service."""
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.graph = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM and graph if API key is available."""
        if settings.openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model,
                    temperature=0.7,

                )
                self.embeddings = OpenAIEmbeddings(
                    api_key=settings.openai_api_key
                )
                # Initialize Pinecone Vector Store
                self.vector_store = LangchainPinecone(
                    index=index,
                    embedding=self.embeddings,
                    namespace=settings.pinecone_name_space,
                    text_key="text"
                )
                self.graph = self._create_conversation_graph()
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.llm = None
                self.embeddings = None
                self.vector_store = None
                self.graph = None
        else:
            print("Warning: OpenAI API key not provided. Chatbot will not function without it.")
    
    def chat_node(self, state: ConversationState) -> ConversationState:
        """Main chat processing node."""
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}

    def build_topic_node(self, state: ConversationState) -> ConversationState:
        """Build the topic node."""
        messages = state["messages"]
        try:
            user_message = messages.pop()
            message = user_message.content
            context = self.get_context(message)

            user_message.content = f"""
            Context: 
            ```md
            {context}
            ```
            Build a structured lesson for beginners about the following users's topic and above context:
            User message:
            {user_message.content}

            --------------------------------
            The Output should be in the following format:
            <h4><topic>Summarized topic from user message</topic></h4>
            <lesson>Generated a lesson as HTML format</lesson>
            --------------------------------
            IMPORTANT:
            - remove <br> tags in output
            """
            messages.append(user_message)
            response = self.llm.invoke(messages)
        except Exception as e:
            print(f"Error building topic: {e}")
            response = "Error building topic"

        return {"messages": [response]}
    
            
    def _create_conversation_graph(self) -> StateGraph:
        """Create and configure the conversation graph."""
        
        
        # Build the graph
        workflow = StateGraph(ConversationState)
        workflow.add_node("chat", self.chat_node)
        workflow.add_node("build_topic", self.build_topic_node)
        

        async def is_touch_lesson(state: ConversationState) -> str:
            """Check if the lesson is touched."""
            # check if the lesson is generated
            lesson_is_generated = False
            conversation = await self.get_conversation(state["conversation_id"])
            for msg in conversation.messages:
                if msg.role == "assistant" and "<lesson>" in msg.content:
                    lesson_is_generated = True
                    break
            
            if lesson_is_generated:
                return "generated"
            else:
                return "not_generated"

        workflow.add_conditional_edges(
            START,
            is_touch_lesson,
            {"not_generated": "build_topic", "generated": "chat"}
        )

        workflow.add_edge("build_topic", END)
        workflow.add_edge("chat", END)
        
        return workflow.compile()
    
    async def create_conversation(self, title: Optional[str] = None) -> str:
        """Create a new conversation and return its ID."""
        print(f"Creating conversation with title: {title}")
        conversation_id = str(uuid.uuid4())
        conversation = ConversationHistory(
            conversation_id=conversation_id,
            messages=[],
            title=title,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Save to MongoDB
        await mongodb_service.save_conversation(conversation)
        return conversation_id
    
    async def get_conversation(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Get conversation history by ID from MongoDB."""
        return await mongodb_service.get_conversation(conversation_id)
    
    def _convert_to_langchain_messages(self, messages: List[ChatMessage]) -> List[BaseMessage]:
        """Convert ChatMessage objects to LangChain message format."""
        langchain_messages = []
        for msg in messages:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content))
        return langchain_messages
    
    def _convert_from_langchain_message(self, message: BaseMessage) -> ChatMessage:
        """Convert LangChain message to ChatMessage format."""
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        else:
            role = "system"
        
        return ChatMessage(
            role=role,
            content=message.content,
            timestamp=datetime.now(timezone.utc)
        )

    async def aget_context(self, message: str) -> str:
        """Get the context for the message."""

        # Retrieve relevant documents from Pinecone using LangChain vector store
        try:
            # Perform similarity search using LangChain Pinecone vector store
            relevant_docs = self.vector_store.similarity_search_with_score(
                query=message,
                k=5,  # top 5 most similar documents
                namespace=settings.pinecone_name_space,
            )
            relevant_docs = [doc for doc, score in relevant_docs if score > 0.9]
        except Exception as e:
            print(f"Error querying Pinecone: {None}")
            relevant_docs = []
            
        logger.info(f"Relevant documents: {len(relevant_docs)}")
        # If no relevant documents, fallback to web search
        if not relevant_docs:
            web_results = await web_search(message)
            context = " ".join(web_results)
        else:
            # Extract content from retrieved documents
            context = " ".join([doc.page_content for doc in relevant_docs])

        return context

    def get_context(self, message: str) -> str:
        """Get the context for the message."""

        # Retrieve relevant documents from Pinecone using LangChain vector store
        try:
            # Perform similarity search using LangChain Pinecone vector store
            relevant_docs = self.vector_store.similarity_search_with_score(
                query=message,
                k=5,  # top 5 most similar documents
                namespace=settings.pinecone_name_space,
            )
            relevant_docs = [doc for doc, score in relevant_docs if score > 0.7]
        except Exception as e:
            print(f"Error querying Pinecone: {None}")
            relevant_docs = []
            
        logger.info(f"Relevant documents: {len(relevant_docs)}")
        # If no relevant documents, fallback to web search
        if not relevant_docs:
            web_results = []# await web_search(message)
            context = " ".join(web_results)
        else:
            # Extract content from retrieved documents
            context = " ".join([doc.page_content for doc in relevant_docs])

        return context
    
    async def chat(self, message: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a chat message using RAG pipeline and return the response.
        """
        # Check if LLM, embeddings, and vector store are initialized
        if not self.llm or not self.embeddings or not self.vector_store or not self.graph:
            raise ValueError("OpenAI client not initialized. Please provide a valid API key.")
        # Create new conversation if none provided
        if not conversation_id:
            conversation_id = await self.create_conversation(message)

        # Get existing conversation or create new one
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            conversation_id = await self.create_conversation(message)
            conversation = await self.get_conversation(conversation_id)

        # Add user message to conversation
        user_message = ChatMessage(
            role="user",
            content=message,
            timestamp=datetime.now(timezone.utc)
        )
        conversation.messages.append(user_message)

        context = await self.aget_context(message)

        # Augment message with context
        augmented_message = f"CONTEXT:\n```md\n{context}\n```\n-------------\nUSER MESSAGE:\n{message}"

        # Convert to LangChain format
        langchain_messages = self._convert_to_langchain_messages(conversation.messages)

        # Process through the graph
        initial_state = ConversationState(
            messages=langchain_messages,
            conversation_id=conversation_id,
            
        )

        # Run the graph
        result = await self.graph.ainvoke(initial_state)

        # Extract the AI response
        ai_response = result["messages"][-1]
        ai_message = self._convert_from_langchain_message(ai_response)

        # Add AI response to conversation
        if conversation.title is None:
            conversation.title = message
        print(f"Conversation title: {conversation.title}")

        conversation.messages.append(ai_message)
        conversation.updated_at = datetime.now(timezone.utc)

        # Save updated conversation to MongoDB
        await mongodb_service.save_conversation(conversation)

        return {
            "message": ai_message.content,
            "conversation_id": conversation_id,
            "model": settings.openai_model,
            "timestamp": ai_message.timestamp
        }
    
    async def get_conversation_history(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get conversation history in a serializable format from MongoDB."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in conversation.messages
        ]
    
    async def list_conversations(self) -> List[Dict[str, Any]]:
        """List all conversations from MongoDB."""
        return await mongodb_service.list_conversations()
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation from MongoDB."""
        return await mongodb_service.delete_conversation(conversation_id)


# Global chatbot service instance
chatbot_service = ChatbotService()