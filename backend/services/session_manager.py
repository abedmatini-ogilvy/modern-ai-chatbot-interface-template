"""
Session Manager - In-Memory Session Storage

Manages research sessions with:
- Session creation and tracking
- Progress storage
- Result caching
- Automatic cleanup of expired sessions

Note: This is in-memory storage for prototype.
For production, replace with database (PostgreSQL, MongoDB, Redis).
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, field
import uuid

from models.research_models import (
    ResearchPhase,
    ProgressUpdate,
    ResearchResultResponse
)


@dataclass
class ResearchSession:
    """Represents a research session"""
    session_id: str
    question: str
    search_query: str
    conversation_id: Optional[str]
    phase: ResearchPhase
    progress_updates: List[ProgressUpdate] = field(default_factory=list)
    result: Optional[ResearchResultResponse] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    task: Optional[asyncio.Task] = None
    error: Optional[str] = None


class SessionManager:
    """
    Manages research sessions in memory.
    
    This is a simple in-memory implementation suitable for prototyping.
    For production, migrate to:
    - PostgreSQL/MongoDB for persistent storage
    - Redis for session caching
    - Task queue (Celery, RQ) for background processing
    """
    
    def __init__(self, session_timeout_minutes: int = 60, max_sessions: int = 100):
        """
        Initialize session manager.
        
        Args:
            session_timeout_minutes: Time before sessions expire
            max_sessions: Maximum concurrent sessions
        """
        self.sessions: Dict[str, ResearchSession] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.max_sessions = max_sessions
        
        # Start background cleanup task
        self._cleanup_task = None
    
    def create_session(
        self,
        question: str,
        search_query: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Create a new research session.
        
        Args:
            question: Research question
            search_query: Search query for APIs
            conversation_id: Optional conversation ID
            
        Returns:
            Session ID
        """
        # Check if we're at capacity
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest completed/failed session
            self._cleanup_old_sessions(force=True)
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Create session
        session = ResearchSession(
            session_id=session_id,
            question=question,
            search_query=search_query,
            conversation_id=conversation_id,
            phase=ResearchPhase.PENDING
        )
        
        self.sessions[session_id] = session
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session or None if not found
        """
        session = self.sessions.get(session_id)
        
        if session:
            # Check if expired
            if datetime.now() - session.updated_at > self.session_timeout:
                self.delete_session(session_id)
                return None
        
        return session
    
    def update_session(
        self,
        session_id: str,
        phase: Optional[ResearchPhase] = None,
        progress_update: Optional[ProgressUpdate] = None,
        result: Optional[ResearchResultResponse] = None,
        error: Optional[str] = None,
        task: Optional[asyncio.Task] = None
    ) -> bool:
        """
        Update session state.
        
        Args:
            session_id: Session identifier
            phase: New phase
            progress_update: Progress update to add
            result: Final result
            error: Error message
            task: Asyncio task
            
        Returns:
            True if updated successfully
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        if phase:
            session.phase = phase
        
        if progress_update:
            session.progress_updates.append(progress_update)
        
        if result:
            session.result = result
            session.phase = result.phase
        
        if error:
            session.error = error
            session.phase = ResearchPhase.FAILED
        
        if task:
            session.task = task
        
        session.updated_at = datetime.now()
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted
        """
        session = self.sessions.get(session_id)
        if session and session.task and not session.task.done():
            session.task.cancel()
        
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        
        return False
    
    def list_sessions(
        self,
        conversation_id: Optional[str] = None,
        phase: Optional[ResearchPhase] = None
    ) -> List[ResearchSession]:
        """
        List sessions with optional filters.
        
        Args:
            conversation_id: Filter by conversation ID
            phase: Filter by phase
            
        Returns:
            List of matching sessions
        """
        sessions = list(self.sessions.values())
        
        if conversation_id:
            sessions = [s for s in sessions if s.conversation_id == conversation_id]
        
        if phase:
            sessions = [s for s in sessions if s.phase == phase]
        
        # Sort by created_at descending
        sessions.sort(key=lambda s: s.created_at, reverse=True)
        
        return sessions
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        return len(self.sessions)
    
    def _cleanup_old_sessions(self, force: bool = False):
        """
        Clean up expired or completed sessions.
        
        Args:
            force: If True, remove oldest session even if not expired
        """
        now = datetime.now()
        expired = []
        
        for session_id, session in self.sessions.items():
            # Remove expired sessions
            if now - session.updated_at > self.session_timeout:
                expired.append(session_id)
            # Remove completed sessions older than 30 minutes
            elif session.phase in [ResearchPhase.COMPLETED, ResearchPhase.FAILED]:
                if now - session.updated_at > timedelta(minutes=30):
                    expired.append(session_id)
        
        for session_id in expired:
            self.delete_session(session_id)
        
        # If forced and still at capacity, remove oldest session
        if force and len(self.sessions) >= self.max_sessions:
            oldest = min(self.sessions.values(), key=lambda s: s.created_at)
            self.delete_session(oldest.session_id)
    
    def start_cleanup_task(self):
        """Start background cleanup task"""
        async def cleanup_loop():
            while True:
                await asyncio.sleep(300)  # Run every 5 minutes
                self._cleanup_old_sessions()
        
        # Create task without awaiting it
        asyncio.create_task(cleanup_loop())
    
    def get_statistics(self) -> Dict:
        """Get session statistics"""
        total = len(self.sessions)
        by_phase = {}
        
        for session in self.sessions.values():
            phase = session.phase.value
            by_phase[phase] = by_phase.get(phase, 0) + 1
        
        return {
            "total_sessions": total,
            "max_sessions": self.max_sessions,
            "by_phase": by_phase,
            "capacity_percentage": round((total / self.max_sessions) * 100, 1)
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    Get or create global session manager instance.
    
    This is a singleton pattern for the session manager.
    """
    global _session_manager
    
    if _session_manager is None:
        from config import settings
        _session_manager = SessionManager(
            session_timeout_minutes=settings.SESSION_TIMEOUT_MINUTES,
            max_sessions=settings.MAX_CONCURRENT_SESSIONS
        )
    
    return _session_manager
