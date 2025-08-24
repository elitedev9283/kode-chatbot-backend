"""
Chat API endpoints.
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import traceback

from app.models.chat import ChatRequest, ChatResponse
from app.services.chatbot import chatbot_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message to the chatbot and receive a response.
    
    Args:
        request: Chat request containing message and optional conversation ID
        
    Returns:
        Chat response with AI message and conversation details
    """
    try:
        result = await chatbot_service.chat(
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            message=result["message"],
            conversation_id=result["conversation_id"],
            model=result["model"],
            timestamp=result["timestamp"]
        )
    
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.post("/conversation", status_code=status.HTTP_201_CREATED)
async def create_conversation(title: Optional[str] = None) -> Dict[str, str]:
    """
    Create a new conversation.
    
    Returns:
        Dictionary containing the new conversation ID
    """
    try:
        conversation_id = await chatbot_service.create_conversation(title)
        return {"conversation_id": conversation_id}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}"
        )


@router.get("/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str) -> Dict[str, Any]:
    """
    Get conversation history by ID.
    
    Args:
        conversation_id: The conversation ID
        
    Returns:
        Dictionary containing conversation history
    """
    try:
        history = await chatbot_service.get_conversation_history(conversation_id)
        conversation = await chatbot_service.get_conversation(conversation_id)
        if history is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "title": conversation.title
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )


@router.get("/conversations")
async def list_conversations() -> Dict[str, List[Dict[str, Any]]]:
    """
    List all conversations.
    
    Returns:
        Dictionary containing list of all conversations
    """
    try:
        conversations = await chatbot_service.list_conversations()
        print(f"Conversations: {conversations}")
        return {"conversations": conversations}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.delete("/conversation/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation.
    
    Args:
        conversation_id: The conversation ID to delete
        
    Returns:
        No content on successful deletion
    """
    try:
        deleted = await chatbot_service.delete_conversation(conversation_id)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )