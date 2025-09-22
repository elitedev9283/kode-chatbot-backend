"""
Chat-related data models.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ChatMessage(BaseModel):
    """Individual chat message model."""
    
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatRequest(BaseModel):
    """Chat request model."""
    
    message: str = Field(..., description="User message", min_length=1)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    model: Optional[str] = Field("gpt-3.5-turbo", description="AI model to use")


class ChatResponse(BaseModel):
    """Chat response model."""
    
    message: str = Field(..., description="AI response message")
    conversation_id: str = Field(..., description="Conversation ID")
    model: str = Field(..., description="AI model used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationHistory(BaseModel):
    """Conversation history model."""
    
    conversation_id: str = Field(..., description="Unique conversation identifier")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))