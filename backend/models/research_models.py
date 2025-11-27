"""
Pydantic Models for Research API

These models define the structure of requests and responses
for the trend research system.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ResearchPhase(str, Enum):
    """Research execution phases"""
    PENDING = "pending"
    DATA_COLLECTION = "data_collection"
    ANALYSIS = "analysis"
    REPORT_GENERATION = "report_generation"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStatus(str, Enum):
    """Status of individual agents"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Research Questions
# ============================================================================

class ResearchQuestion(BaseModel):
    """Pre-configured research question"""
    id: str = Field(..., description="Unique identifier for the question")
    title: str = Field(..., description="Short title for the question")
    question: str = Field(..., description="Full research question text")
    focus: str = Field(..., description="Focus areas for research")
    search_terms: List[str] = Field(..., description="Search terms for APIs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "gen_z_nigeria",
                "title": "Gen Z Nigeria: Facebook vs Google Usage",
                "question": "Why does Gen Z in Nigeria appear to use Facebook for community...",
                "focus": "Social behavior patterns, platform preferences",
                "search_terms": ["Gen Z Nigeria Facebook", "Nigeria Google usage"]
            }
        }


# ============================================================================
# Request Models
# ============================================================================

class ResearchStartRequest(BaseModel):
    """Request to start a new research session"""
    question: Optional[str] = Field(None, description="Research question to investigate (required if question_id not provided)")
    search_query: Optional[str] = Field(None, description="Custom search query for APIs")
    question_id: Optional[str] = Field(None, description="ID of pre-configured question")
    conversation_id: Optional[str] = Field(None, description="Associated conversation ID")
    max_results: Optional[int] = Field(50, description="Max results per API", ge=10, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the emerging trends in African e-commerce?",
                "search_query": "African e-commerce trends 2024",
                "max_results": 50
            }
        }


# ============================================================================
# Progress Models
# ============================================================================

class ProgressUpdate(BaseModel):
    """Progress update during research execution"""
    timestamp: datetime = Field(default_factory=datetime.now)
    phase: ResearchPhase = Field(..., description="Current research phase")
    agent: Optional[str] = Field(None, description="Name of agent reporting progress")
    status: AgentStatus = Field(..., description="Status of the agent")
    message: str = Field(..., description="Human-readable progress message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional progress data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-01-01T12:00:00",
                "phase": "data_collection",
                "agent": "Twitter Intelligence Agent",
                "status": "completed",
                "message": "✅ Found 50 tweets with sentiment analysis",
                "data": {"tweets_collected": 50}
            }
        }


# ============================================================================
# Response Models
# ============================================================================

class ResearchStatusResponse(BaseModel):
    """Response for research status check"""
    session_id: str = Field(..., description="Unique session identifier")
    phase: ResearchPhase = Field(..., description="Current research phase")
    progress_percentage: int = Field(..., description="Overall progress (0-100)", ge=0, le=100)
    current_agent: Optional[str] = Field(None, description="Currently active agent")
    progress_updates: List[ProgressUpdate] = Field(default_factory=list, description="Progress history")
    started_at: datetime = Field(..., description="Session start time")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "phase": "data_collection",
                "progress_percentage": 40,
                "current_agent": "Reddit Intelligence Agent",
                "progress_updates": [],
                "started_at": "2024-01-01T12:00:00"
            }
        }


class ResearchResultResponse(BaseModel):
    """Response with complete research results"""
    session_id: str = Field(..., description="Unique session identifier")
    question: str = Field(..., description="Original research question")
    search_query: str = Field(..., description="Search query used")
    
    # Execution metadata
    phase: ResearchPhase = Field(..., description="Final phase status")
    started_at: datetime = Field(..., description="Research start time")
    completed_at: Optional[datetime] = Field(None, description="Research completion time")
    execution_time_seconds: Optional[float] = Field(None, description="Total execution time")
    
    # Collected data summary
    data_collected: Dict[str, Any] = Field(default_factory=dict, description="Summary of collected data")
    total_data_points: int = Field(0, description="Total data points collected")
    failed_apis: List[str] = Field(default_factory=list, description="APIs that failed")
    
    # Analysis results
    insights: Optional[str] = Field(None, description="Analyzed insights from data")
    report: Optional[str] = Field(None, description="Full research report")
    
    # Report sections (for multi-message display)
    executive_summary: Optional[str] = Field(None, description="Executive summary section")
    key_findings: Optional[List[str]] = Field(None, description="Key findings as bullet points")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations as bullet points")
    
    # Progress history
    progress_updates: List[ProgressUpdate] = Field(default_factory=list, description="All progress updates")
    
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc123",
                "question": "What are emerging trends in African e-commerce?",
                "search_query": "African e-commerce trends",
                "phase": "completed",
                "started_at": "2024-01-01T12:00:00",
                "completed_at": "2024-01-01T12:05:00",
                "execution_time_seconds": 300.5,
                "total_data_points": 250,
                "insights": "Analysis of collected data...",
                "report": "Full comprehensive report...",
                "progress_updates": []
            }
        }
