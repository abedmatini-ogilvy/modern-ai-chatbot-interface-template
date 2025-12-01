"""
Research API Router

Endpoints for conducting trend research:
- POST /api/research/start - Start new research
- GET /api/research/{session_id}/status - Get progress
- GET /api/research/{session_id}/result - Get final result
- GET /api/research/questions - List pre-configured questions
- GET /api/research/sessions - List active sessions
"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional

from models.research_models import (
    ResearchQuestion,
    ResearchStartRequest,
    ResearchStatusResponse,
    ResearchResultResponse,
    ResearchPhase,
    ProgressUpdate
)
from services.research_service import ResearchService
from services.session_manager import get_session_manager
from config import settings

# Create router
router = APIRouter(prefix="/api/research", tags=["research"])

# Initialize research service
research_service = ResearchService(
    azure_api_key=settings.AZURE_AI_API_KEY,
    azure_endpoint=settings.AZURE_AI_ENDPOINT
)


# ============================================================================
# Helper Functions
# ============================================================================

async def run_research_task(
    session_id: str,
    question: str,
    search_query: str,
    max_results: int
):
    """
    Background task to run research.
    
    This runs asynchronously and updates the session as it progresses.
    """
    session_manager = get_session_manager()
    
    def progress_callback(update: ProgressUpdate):
        """Callback to store progress updates"""
        session_manager.update_session(
            session_id=session_id,
            progress_update=update
        )
    
    try:
        # Update phase to data collection
        session_manager.update_session(
            session_id=session_id,
            phase=ResearchPhase.DATA_COLLECTION
        )
        
        # Run research
        result = await research_service.conduct_research(
            question=question,
            search_query=search_query,
            session_id=session_id,
            progress_callback=progress_callback,
            max_results=max_results
        )
        
        # Store result
        session_manager.update_session(
            session_id=session_id,
            result=result
        )
        
    except Exception as e:
        session_manager.update_session(
            session_id=session_id,
            error=str(e),
            phase=ResearchPhase.FAILED
        )


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/start", response_model=dict)
async def start_research(
    request: ResearchStartRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new research session.
    
    This endpoint initiates the research process and returns a session ID
    that can be used to check progress and retrieve results.
    
    The research runs in the background, so this endpoint returns immediately.
    """
    session_manager = get_session_manager()
    
    # Check capacity
    if session_manager.get_session_count() >= settings.MAX_CONCURRENT_SESSIONS:
        raise HTTPException(
            status_code=503,
            detail="Server at capacity. Please try again later."
        )
    
    # Determine search query and question
    search_query = request.search_query
    question = request.question
    
    # If using a pre-configured question, get its details
    if request.question_id:
        pre_configured = research_service.get_research_question(request.question_id)
        if not pre_configured:
            raise HTTPException(status_code=404, detail="Question ID not found")
        
        question = pre_configured["question"]
        if not search_query:
            search_query = pre_configured["search_terms"][0]
    
    # Validate we have both question and search query
    if not question:
        raise HTTPException(
            status_code=400,
            detail="Either 'question' or 'question_id' must be provided"
        )
    
    if not search_query:
        raise HTTPException(
            status_code=400,
            detail="search_query is required when not using a pre-configured question"
        )
    
    # Create session
    session_id = session_manager.create_session(
        question=question,
        search_query=search_query,
        conversation_id=request.conversation_id
    )
    
    # Start research task in background
    task = asyncio.create_task(
        run_research_task(
            session_id=session_id,
            question=question,
            search_query=search_query,
            max_results=request.max_results or settings.DEFAULT_MAX_RESULTS
        )
    )
    
    # Store task reference
    session_manager.update_session(session_id=session_id, task=task)
    
    return {
        "session_id": session_id,
        "message": "Research started successfully",
        "question": question,
        "search_query": search_query,
        "status_url": f"/api/research/{session_id}/status",
        "result_url": f"/api/research/{session_id}/result"
    }


@router.get("/{session_id}/status", response_model=ResearchStatusResponse)
async def get_research_status(session_id: str):
    """
    Get the current status of a research session.
    
    This endpoint returns:
    - Current phase (pending, data_collection, analysis, etc.)
    - Progress percentage
    - All progress updates so far
    - Estimated completion time
    
    Poll this endpoint to get real-time updates.
    """
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate progress percentage
    progress_percentage = 0
    if session.phase == ResearchPhase.PENDING:
        progress_percentage = 0
    elif session.phase == ResearchPhase.DATA_COLLECTION:
        # During data collection, estimate based on progress updates
        progress_percentage = min(40, len(session.progress_updates) * 5)
    elif session.phase == ResearchPhase.ANALYSIS:
        progress_percentage = 60
    elif session.phase == ResearchPhase.REPORT_GENERATION:
        progress_percentage = 80
    elif session.phase == ResearchPhase.COMPLETED:
        progress_percentage = 100
    elif session.phase == ResearchPhase.FAILED:
        progress_percentage = 0
    
    # Get current agent from latest progress update
    current_agent = None
    if session.progress_updates:
        latest = session.progress_updates[-1]
        if latest.agent:
            current_agent = latest.agent
    
    # Estimate completion (very rough estimate)
    estimated_completion = None
    if session.phase not in [ResearchPhase.COMPLETED, ResearchPhase.FAILED]:
        # Assume ~30 seconds average completion time
        from datetime import timedelta
        estimated_completion = session.created_at + timedelta(seconds=settings.RESEARCH_TIMEOUT_SECONDS / 2)
    
    return ResearchStatusResponse(
        session_id=session_id,
        phase=session.phase,
        progress_percentage=progress_percentage,
        current_agent=current_agent,
        progress_updates=session.progress_updates,
        started_at=session.created_at,
        estimated_completion=estimated_completion,
        error=session.error
    )


@router.get("/{session_id}/result", response_model=ResearchResultResponse)
async def get_research_result(session_id: str):
    """
    Get the final result of a completed research session.
    
    This endpoint returns:
    - Full research report
    - Executive summary
    - Key findings and recommendations
    - All collected data
    - Execution metrics
    
    Only available when research is completed.
    """
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.phase == ResearchPhase.FAILED:
        raise HTTPException(
            status_code=500,
            detail=f"Research failed: {session.error or 'Unknown error'}"
        )
    
    if session.phase != ResearchPhase.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Research not yet completed. Current phase: {session.phase.value}"
        )
    
    if not session.result:
        raise HTTPException(
            status_code=500,
            detail="Research completed but no result available"
        )
    
    return session.result


@router.get("/questions", response_model=List[ResearchQuestion])
async def list_research_questions():
    """
    Get list of pre-configured research questions.
    
    These questions are ready-to-use and include:
    - Optimized search terms
    - Focus areas
    - Detailed question text
    
    Use the 'id' field in the start request to use these questions.
    """
    questions = research_service.get_research_questions()
    return [
        ResearchQuestion(
            id=q["id"],
            title=q["title"],
            question=q["question"],
            focus=q["focus"],
            search_terms=q["search_terms"]
        )
        for q in questions
    ]


@router.get("/sessions", response_model=List[dict])
async def list_sessions(
    conversation_id: Optional[str] = None,
    phase: Optional[ResearchPhase] = None
):
    """
    List active research sessions.
    
    Optional filters:
    - conversation_id: Get sessions for a specific conversation
    - phase: Filter by research phase
    
    Useful for:
    - Resuming conversations
    - Monitoring active research
    - Debugging
    """
    session_manager = get_session_manager()
    sessions = session_manager.list_sessions(
        conversation_id=conversation_id,
        phase=phase
    )
    
    return [
        {
            "session_id": s.session_id,
            "question": s.question,
            "search_query": s.search_query,
            "conversation_id": s.conversation_id,
            "phase": s.phase,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "progress_count": len(s.progress_updates),
            "has_result": s.result is not None
        }
        for s in sessions
    ]


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a research session.
    
    This will:
    - Cancel any running research task
    - Remove all session data
    - Free up capacity
    """
    session_manager = get_session_manager()
    
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}


@router.get("/statistics")
async def get_statistics():
    """
    Get session statistics.
    
    Returns:
    - Total active sessions
    - Sessions by phase
    - Capacity utilization
    
    Useful for monitoring and debugging.
    """
    session_manager = get_session_manager()
    return session_manager.get_statistics()
