from contextlib import asynccontextmanager
import fastapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import uvicorn
import time

# Import routers
from src.api import outfits, color, try_on, auth, user_outfits, user_color, shape, user_info
from src.database.user_db import init_db
from src.utils.logger import get_logger

logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Hack Seoul API...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise
    
    logger.info("API startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down Hack Seoul API...")


app = fastapi.FastAPI(
    title="Hack Seoul Fashion API",
    description="Personal color analysis and outfit try-on API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()
    
    # Log request
    logger.info(
        f"Request: {request.method} {request.url.path} - "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Error processing request: {request.method} {request.url.path} - "
            f"Error: {str(e)} - Time: {process_time:.3f}s",
            exc_info=True
        )
        raise

# Include routers
app.include_router(outfits.router)
app.include_router(color.router)
app.include_router(try_on.router)
app.include_router(auth.router)
app.include_router(user_outfits.router)
app.include_router(user_color.router)
app.include_router(shape.router)
app.include_router(user_info.router)


@app.get("/")
def read_root():
    """
    Root endpoint - API health check.
    """
    logger.debug("Health check endpoint accessed")
    return {"message": "Let's win Hack Seoul! I need more money, please im broke!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
