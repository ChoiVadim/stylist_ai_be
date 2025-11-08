import fastapi
import uvicorn

# Import routers
from src.api import outfits, color, try_on

app = fastapi.FastAPI(
    title="Hack Seoul Fashion API",
    description="Personal color analysis and outfit try-on API",
    version="1.0.0"
)

# Include routers
app.include_router(outfits.router)
app.include_router(color.router)
app.include_router(try_on.router)


@app.get("/")
def read_root():
    """
    Root endpoint - API health check.
    """
    return {"message": "Let's win Hack Seoul! I need more money, please im broke!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
