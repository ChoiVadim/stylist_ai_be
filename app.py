from contextlib import asynccontextmanager
import fastapi
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from src.api import outfits, color, try_on, auth, user_outfits, user_color, shape
from src.database.user_db import init_db


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    init_db()
    yield
    # Shutdown (if needed in the future)
    pass


app = fastapi.FastAPI(
    title="Hack Seoul Fashion API",
    description="Personal color analysis and outfit try-on API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(outfits.router)
app.include_router(color.router)
app.include_router(try_on.router)
app.include_router(auth.router)
app.include_router(user_outfits.router)
app.include_router(user_color.router)
app.include_router(shape.router)


@app.get("/")
def read_root():
    """
    Root endpoint - API health check.
    """
    return {"message": "Let's win Hack Seoul! I need more money, please im broke!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
