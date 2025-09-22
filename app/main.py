"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.chat import router as chat_router
from app.services.mongodb import mongodb_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    print("🚀 Starting Chatbot API...")
    print(f"📝 OpenAI API Key configured: {'✅' if settings.openai_api_key else '❌'}")
    print(f"🗄️  MongoDB URI: {settings.mongodb_uri}")
    print(f"📊 MongoDB Database: {settings.mongodb_database}")
    print(f"📁 MongoDB Collection: {settings.mongodb_collection}")
    yield
    # Shutdown
    print("🛑 Shutting down Chatbot API...")
    await mongodb_service.close()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        debug=settings.debug,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.allowed_credentials,
        allow_methods=settings.allowed_methods,
        allow_headers=settings.allowed_headers,
    )
    
    # Include routers
    app.include_router(chat_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to the Chatbot API!",
            "version": settings.api_version,
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.api_version,
            "openai_configured": bool(settings.openai_api_key),
            "mongodb_configured": bool(settings.mongodb_uri)
        }
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )