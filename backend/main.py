"""
FastAPI Backend for Trend Research System

This is the main entry point for the FastAPI application.
It provides REST APIs for the Next.js frontend to conduct
multi-agent trend research with real-time progress updates.

Architecture:
- Multiple endpoints for research lifecycle
- In-memory session storage (ready for database migration)
- CORS enabled for Next.js frontend
- Mock API connectors (switchable to real APIs)

Start server:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

API Documentation:
    http://localhost:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from config import settings
from routers.research_router import router as research_router
from routers.chat_router import router as chat_router
from services.session_manager import get_session_manager

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-agent trend research system API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research_router)
app.include_router(chat_router)


# ============================================================================
# Health Check & Info Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    
    # Check Azure OpenAI configuration
    azure_status = "configured" if settings.azure_openai_configured else "not_configured"
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "operational",
            "azure_openai": azure_status,
            "session_manager": "operational",
            "research_service": "operational"
        },
        "configuration": {
            "debug_mode": settings.DEBUG,
            "max_concurrent_sessions": settings.MAX_CONCURRENT_SESSIONS,
            "session_timeout_minutes": settings.SESSION_TIMEOUT_MINUTES
        }
    }


@app.get("/api/config")
async def get_config():
    """Get public configuration information"""
    return {
        "azure_openai_configured": settings.azure_openai_configured,
        "default_max_results": settings.DEFAULT_MAX_RESULTS,
        "research_timeout_seconds": settings.RESEARCH_TIMEOUT_SECONDS,
        "model_name": settings.AZURE_AI_MODEL_NAME if settings.azure_openai_configured else None
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors"""
    if settings.DEBUG:
        # In debug mode, return detailed error
        return JSONResponse(
            status_code=500,
            content={
                "error": str(exc),
                "type": type(exc).__name__,
                "timestamp": datetime.now().isoformat()
            }
        )
    else:
        # In production, return generic error
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "timestamp": datetime.now().isoformat()
            }
        )


# ============================================================================
# Application Lifecycle
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📡 Server: {settings.HOST}:{settings.PORT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"🤖 Azure OpenAI: {'✅ Configured' if settings.azure_openai_configured else '❌ Not Configured'}")
    print(f"💬 Chat API: ✅ Enabled (Gemini)")
    print(f"📚 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    
    # Start session cleanup task
    session_manager = get_session_manager()
    session_manager.start_cleanup_task()
    print("🧹 Session cleanup task started")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"👋 Shutting down {settings.APP_NAME}")
    # Cleanup sessions, close connections, etc.


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print(f"\n{'='*60}")
    print(f"  {settings.APP_NAME} - Starting Development Server")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
