"""
Chat API Router

Endpoints for conversational AI:
- POST /api/chat - Send a message and get AI response
- DELETE /api/chat/{conversation_id} - Clear conversation history
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from services.chat_service import get_chat_service, ChatAction

# Create router
router = APIRouter(prefix="/api/chat", tags=["chat"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Request to send a chat message"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    conversation_id: str = Field(..., description="Unique conversation identifier")


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    action: str = Field(..., description="Action type: respond, research, or clarify")
    message: str = Field(..., description="AI's response message")
    research_question: Optional[str] = Field(None, description="Research question if action is 'research'")
    search_query: Optional[str] = Field(None, description="Search terms if action is 'research'")
    timestamp: str = Field(..., description="Response timestamp")


class ClearHistoryResponse(BaseModel):
    """Response from clearing history"""
    success: bool
    message: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the AI assistant.
    
    The AI will:
    1. Respond conversationally to greetings and questions
    2. Explain platform capabilities when asked
    3. Detect research requests and return action='research' with query details
    4. Ask for clarification if the request is unclear
    
    Returns:
        ChatResponse with action type and message
    """
    chat_service = get_chat_service()
    
    try:
        result = await chat_service.chat(
            conversation_id=request.conversation_id,
            message=request.message
        )
        
        return ChatResponse(
            action=result.action.value,
            message=result.message,
            research_question=result.research_question,
            search_query=result.search_query,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat service error: {str(e)}"
        )


@router.delete("/{conversation_id}", response_model=ClearHistoryResponse)
async def clear_history(conversation_id: str):
    """
    Clear conversation history for a specific conversation.
    
    This removes all stored messages for the conversation,
    allowing a fresh start.
    """
    chat_service = get_chat_service()
    
    try:
        chat_service.clear_history(conversation_id)
        return ClearHistoryResponse(
            success=True,
            message=f"Conversation history cleared for {conversation_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear history: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """Check chat service health"""
    chat_service = get_chat_service()
    
    return {
        "status": "healthy",
        "llm_available": chat_service.llm_connector is not None,
        "active_conversations": len(chat_service.conversations)
    }
